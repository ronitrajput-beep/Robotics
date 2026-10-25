"""Check the preserved faculty controls, visible PDF content and page bounds."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib,json
import fitz

ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def controls(path):
    with ZipFile(path) as archive:r=E.fromstring(archive.read('word/document.xml'))
    result={}
    for sdt in r.xpath('//w:sdt',namespaces=NS):
        tag=sdt.find('w:sdtPr/w:tag',NS).get(W+'val')
        result[tag]={'choices':[(i.get(W+'value'),i.get(W+'displayText')) for i in sdt.findall('w:sdtPr/w:dropDownList/w:listItem',NS)],'text':''.join(sdt.xpath('./w:sdtContent//w:t/text()',namespaces=NS))}
    return result

def check():
    original=ROOT/'submission/templates/MDRIIA_Group_06_Technical_Dossier_original.docx';word=ROOT/'docs/MDRIIA_Group_06_Technical_Dossier.docx';pdf=word.with_suffix('.pdf')
    old=controls(original);new=controls(word);audit=json.loads((ROOT/'submission/dossier_field_audit.json').read_text())
    assert set(old)==set(new) and len(new)==212
    assert all(old[k]['choices']==new[k]['choices'] for k in old)
    assert all(new[k]['text'] not in ('','type here') for k in new)
    assert sha(word)==audit['dossier_sha256'],'Word changed since field audit; regenerate or review intentionally'
    document=fitz.open(pdf);text=''.join(''.join(p.get_text().split()) for p in document)
    for required in ['83.385','28.519','SIGNPERSONALLY','AppendixA','AppendixB','AppendixC','10.1109/IROS.2012.6386109']:
        assert required in text,f'Missing/clipped PDF content: {required}'
    assert ('PRELIMINARYREVIEWCOPY' in text)==audit['preliminary']
    out_of_bounds=[]
    for i,page in enumerate(document):
        for wordbox in page.get_text('words'):
            x0,y0,x1,y1,*_=wordbox
            if x0<-1 or y0<-1 or x1>page.rect.width+1 or y1>page.rect.height+1:out_of_bounds.append({'page':i+1,'word':wordbox[4],'bounds':[x0,y0,x1,y1]})
    assert not out_of_bounds,out_of_bounds[:5]
    assert sum(len(p.get_images()) for p in document)>=5,'Figures missing from PDF'
    report={'pass':True,'preliminary':audit['preliminary'],'content_controls_preserved':212,'personal_controls_pending':len(audit['human_fields_pending']),'pdf_pages':len(document),'worked_example_visible':True,'text_within_page_bounds':True,'word_sha256':sha(word),'pdf_sha256':sha(pdf),'human_actions':'Member authorship/learning/declarations, actual peer reviews, team video/LinkedIn, personal signatures and faculty/Teams turn-in remain required.'}
    (ROOT/'submission/deliverable_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report

if __name__=='__main__':check()
