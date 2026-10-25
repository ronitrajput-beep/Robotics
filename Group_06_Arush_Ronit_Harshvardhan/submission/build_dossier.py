"""Fill the faculty's original Word controls without replacing the form.

Use --preliminary only while the frozen final experiment is still running.
Personal declarations stay highlighted until members complete them themselves.
"""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, hashlib, json, math, sys
from lxml import etree as E
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}
def wt(name):return '{'+W+'}'+name
def read(path):return json.loads((ROOT/path).read_text())
def num(value,digits=4):return 'unavailable' if value is None else f'{value:.{digits}g}'
def mean_sd(metric):return f"{num(metric['mean'],6)} ± {num(metric['sd'],3)}"

REFERENCES=[
 ('[1] E. Todorov, T. Erez and Y. Tassa, “MuJoCo: A physics engine for model-based control,” IROS, pp. 5026–5033, 2012. DOI: 10.1109/IROS.2012.6386109.', 'MuJoCo simulator context; developer README citation metadata verified.'),
 ('[2] W. F. Holmgren, C. W. Hansen and M. A. Mikofski, “pvlib python: a python package for modeling solar energy systems,” JOSS 3(29), 884, 2018. DOI: 10.21105/joss.00884.', 'PV modelling software context; official README metadata, not a PV-yield calculation in this project.'),
 ('[3] K. S. Anderson et al., “pvlib python: 2023 project update,” JOSS 8(92), 5994, 2023. DOI: 10.21105/joss.05994.', 'PV modelling context; official README metadata verified.'),
 ('[4] M. G. Deceglie, L. Micheli and M. Muller, “Quantifying Soiling Loss Directly From PV Yield,” IEEE Journal of Photovoltaics 8(2), pp. 547–551, 2018. DOI: 10.1109/JPHOTOV.2017.2784682.', 'Yield-based soiling measurement is separate from a dust-removal proxy; author-maintained rdtools README metadata only, full article not accessed.'),
 ('[5] D. C. Jordan et al., “Robust PV Degradation Methodology and Application,” IEEE Journal of Photovoltaics 8(2), pp. 525–531, 2018. DOI: 10.1109/JPHOTOV.2017.2779779.', 'Yield/degradation analysis context; author-maintained rdtools README metadata only, full article not accessed.'),
]

def values(preliminary):
    nominal=read('analytics/collection_pilot8/result.json');p=nominal['physical_mission'];inventory=nominal['collection']
    business_dir='analytics/business_nominal_draft_v1' if preliminary else 'analytics/final_business_v1'
    business=read(business_dir+'/results.json');b=business['base_case'];a=business['assumptions'];measured=business['measured']
    v={}
    def put(section,**fields):v.update({f'M06.{section}.{k}':str(value) for k,value in fields.items()})
    reasons=[
      'No verified site-specific yield source obtained; delete numerical Mumbai claim. No electrical PV model is implemented.',
      'No verified primary monthly-loss source obtained. Monthly loss cannot be multiplied by annual generation as an annual-average loss; delete.',
      'No measured PV electrical recovery or sourced commercial payback supports these numbers. Delete; replace with explicitly assumed dimensionless scenario in Section 3.'
    ]
    for i,reason in enumerate(reasons,1):
        put('S1',**{f'claim{i}.source':reason,f'claim{i}.source_type':'No source found',f'claim{i}.verdict':'Delete'})
    for tag,reason in {
        'std_iso10218':'Scope: industrial robot/manipulator and integration. This fixed-panel cleaning mobile device is not an industrial manipulator; no conformity claim.',
        'std_iso3691':'Scope: driverless industrial trucks. The selected fixed PV-bay cleaner is not an industrial truck; no conformity claim.',
        'std_ria':'Industrial robot-system standard associated with ISO 10218; selected system is not an industrial manipulator. No compliance claim.',
        'std_iec60601':'Medical electrical equipment; the PV cleaner has no medical use. No applicable medical requirement.'
    }.items():put('S1',**{tag+'.applies':'No',tag+'.clause':reason})
    put('S1',**{'std_domain.applies':'Partly','std_domain.clause':'IEC 61215 (PV module qualification) and IEC 61730 (module safety) are relevant to future module/cleaner compatibility. Licensed clauses and allowable local brush/wheel loads were not verified; no clause number, certified glass load or compliance is asserted.'})
    put('S1',baseline_value='Measured simulation baseline: waypoint + proportional wheel control; compare at equal 0–30 s exposure. Commercial reference: 120 person-hours/month is an assumption, not a site measurement.',baseline_source='Actual controller logs and frozen protocol; commercial assumptions in analytics/final_business_inputs.json. No Mumbai field survey or verified annual-yield figure.',stakeholder='Rooftop PV owner/operator and cleaning contractor; access, inspection, transfer and maintenance remain human responsibilities in the business scenario.')
    put('S2',timestep='0.002 s; 500 Hz integration and logging',friction='Rollers 1.2 / 0.005 / 0.0001; glass and brush 0.4 / 0.005 / 0.0001; brush contact priority 2. Guard friction is zero. These are model assumptions, not measured tyre/glass properties.',solref='Brush/glass 0.02 s, 1 (soft bristle approximation); guide 0.01 s, 1; model default 0.005 s, 1. Rounded capsule contact was retained after replay rejected rigid-cylinder kicks. No coating-safety inference.',control_law='PI / PD',gains='Wheel PI: Kp=0.8 N·m/(rad/s), Ki=0.5 N·m/rad, integral clamp ±3 rad, motor ±3 N·m. Heading 3 s⁻¹, yaw command ±1.2 rad/s. Shared incline/return regulator Kp=0.6, Ki=0.2; torque ±1 N·m, slew 4 N·m/s. Brush velocity target 15 rad/s, kv=0.1, torque ±1 N·m.',fsm_states='HOME_MONITOR → SETTLE/ALIGN → SWEEP; image-requested EDGE_CLEAN_BOTTOM; verification/revisit; RETURN_HOME → DOCKING → DOCK_SERVICE → DOCKED. Safety abort/timeout remain failed outcomes.',model_loads='Yes')
    changes=[
       'Active model is collection_cleaning_crawler.xml: off-glass dock, capsule brush, fixed support/guide, tray; 8.5 kg robot and 5 actuators. AI-assisted development; member authorship pending.',
       'Camera-gated departure, PI tracking, safe turns/return, contact-gated brush, 500 Hz actual torque logging. AI-assisted; member authorship pending.',
       'Replaced unsupported PV percentages with measured-throughput, dimensionless scenario, explicit human transfer labour and sensitivity. Member authorship pending.',
       'Real rendered RGB observations, persistence gate, camera-target revisits and final independent scoring. Ground-truth navigation disclosed; member authorship pending.',
       'Frozen 180 full-mission attempts over 3 tilts with independent seeds, raw torques and source snapshots; no generated targets. Member authorship pending.'
    ]
    for i,change in enumerate(changes,1):put('S2',**{f'script{i}.change':change})
    put('S2',**{'script4.name':'src/vision_mission.py + panel_vision.py','script5.name':'src/run_final_validation.py'})
    qualifier='PROVISIONAL calibration: one validated nominal run; final batch pending. ' if preliminary else 'All 30 proposed attempts at 20°, failures retained. '
    put('S3.E058',hreclaimed_inputs=qualifier+f"H0={a['manual_person_hours_per_month']} h/month; {a['sections_per_day']} sections/day × {a['operating_days_per_month']} days; f={a['supervision_fraction']}; attempt mean {num(measured['mean_attempt_s'],6)} s; p={num(measured['success_fraction'])}; transfer=180 s/section fully human; recovery=180 s/failure fully human; maintenance=10 h/month. All commercial values are assumptions.",hreclaimed_metric=f"{num(b['labour_reclaimed_person_h_month'],6)} person-h/month; robot-related human effort {num(b['total_robot_related_person_h_month'],6)} h/month (monitoring + transfer/recovery + maintenance).",payback_inputs='Normalise one year of baseline labour cost to 1. CapEx ratio k=0.65; life L=5 years; annual saving ratio s=NCRI. All commercial inputs assumed. T=12k/s months; P=k/(L·s); undefined for s≤0.',payback_metric=f"T={num(b['payback_months'],5)} months; P={num(b['lifetime_normalised_payback'],5)} (dimensionless). Scenario output, not observed payback.",ncri_inputs='κ=human-hours/H0 + annual energy cost ratio + 0.05 spares/battery + 0.03 consumables. Electrical estimate: positive simulated work/assumed 0.60 efficiency + 20 W modelled blower + 5 W electronics; two assumed 3 W cameras. Tariff ratio=0.0003 per kWh of one-year baseline cost.',ncri_metric=f"κ={num(b['kappa'],5)}; NCRI=1−κ={num(b['NCRI'],5)}. Estimated system energy {num(b['estimated_system_kWh_year'],5)} kWh/year under scenario assumptions; not measured electrical energy.",queue_inputs=f"A section is one 24 m² bay, not a raster lane. λ={num(b['arrival_rate_sections_h'])} sections/h; μ=3600/[E(Tattempt)/p + (1−p)·180/p + 180]={num(b['service_rate_sections_h'],6)} sections/h; c=1. Poisson arrivals/exponential service assumed.",queue_metric=f"ρ={num(b['utilisation'],5)}; Wq={num(b['queue_wait_h']*60 if b['queue_wait_h'] is not None else None,5)} min if stable. Mean service {num(b['service_mean_s'],6)} s. M/M/1 distribution assumptions are not validated by the simulator.",sensitivity_inputs='Eight inputs swept ±30%: supervision, baseline hours, CapEx, manual transfer, failure recovery, energy price ratio, maintenance and drive efficiency. Repeated independent retries are an assumption. See sensitivity.csv; no PV yield uplift is monetised.',sensitivity_metric=f"Break-even supervision fraction f={num(b['break_even_supervision_fraction'],5)}; maximum k for payback within assumed life={num(b['maximum_capital_ratio_for_payback_within_life'],5)}. Negative NCRI and unstable queues are retained, not converted to finite payback.",queue_model='M/M/1',queue_params=f"λ={num(b['arrival_rate_sections_h'])} sections/h; μ={num(b['service_rate_sections_h'],6)} sections/h; c=1; ρ={num(b['utilisation'],5)}",payback_months=f"{num(b['payback_months'],6)} months; assumed scenario",reproducible='Yes')
    fmeas=[
      ('Crawler slides down-slope on dusty glass (loss of traction)','Fall/damage, interrupted work and human recovery.',9,4,8,'Physical containment guard, bounded return drive, attitude/height stop and logged guard load; guards remain part of the safety model. Post D=3 credits simulation fault detection only.',3,'Both'),
      ('Brush scratches anti-reflective coating','Permanent PV damage and repair cost.',8,4,9,'Rounded soft-contact brush and load logs support development. Coating wear, grit hardness and allowable local pressure are unvalidated. No reduction credited: post S/O/D unchanged.',9,'Not yet'),
      ('RGB misses dirt or falsely declares clean','Residual dirt or wasted cleaning cycle.',6,5,8,'Persistent two-frame image trigger; actual camera feeds; independent final residual check rejects false-clean development cases. Post D=3 is offline evaluation detectability, not field camera reliability.',3,'Both'),
      ('Large solid escapes or jams the guide','Unsafe ejection, jam or incomplete mission.',7,4,7,'Permanent tray, fixed guide and actual solid/contact logs; success requires final retention. Applies only to the tested lower-strip corridor. Post D=3 credits final logged check.',3,'Both'),
      ('Dock transfer/accounting fault','Dirt inventory error or missed service.',5,4,7,'Settled docking, 8 s modelled service, explicit mass balance and charge-energy counters. Post D=3 credits software checks; no airflow, connector or battery hardware reliability claim.',3,'Both')
    ]
    for i,(mode,effect,s,o,d,mitigation,postd,evidence) in enumerate(fmeas,1):
        fields={f'fmea{i}.{k}':value for k,value in dict(effect=effect,severity=s,occurrence=o,detection=d,rpn_pre=s*o*d,mitigation=mitigation,rpn_post=s*o*postd,evidence=evidence).items()}
        if i>=3:fields[f'fmea{i}.mode']=mode
        put('S3',**fields)
    put('S4',log_rate_hz='500 Hz; each 0.002 s integration sample. XZ compresses CSV; final batch serialises numbers to 9 significant digits.',seeds_recorded='Yes',test="Welch's t-test",prov_own_runs='Yes',prov_no_simulated='Yes',prov_plots_reproducible='Yes',prov_economics_sourced='Yes')
    if preliminary:
        stats=read('analytics/tracking_benchmark/statistics.json')
        put('S4',baseline_condition='PRELIMINARY: historical 30 s initial-sweep study on the earlier model, baseline waypoint/P vs proposed lookahead/PI. This is not a final collection-system study. A separate frozen 180 full-mission batch is running; do not merge datasets.',n_runs='Historical study: 30 baseline + 30 proposed at nominal 20°. Final model: planned 30/controller/tilt × 10°,20°,30° = 180; pending.',randomised='Historical protocol records independent initial-pose seeds. Final protocol: initial x/y U(−0.01,+0.01) m and independent dust shape/offset seed; dry friction fixed. No wet-glass/random-colour challenge is claimed.',real_csv_path='Historical: analytics/tracking_benchmark/*_real_trials.csv (see protocol.json). Pending final: analytics/final_validation_v1/tilt_*/{variant}_{seed}/telemetry.csv.xz.',**{'rmse.n':'30 per controller; historical only','rmse.baseline':f"{stats['baseline_mean_m']:.7f} ± {stats['baseline_sd_m']:.7f}",'rmse.proposed':f"{stats['proposed_mean_m']:.7f} ± {stats['proposed_sd_m']:.7f}",'rmse.unit':'m; 0–30 s geometric error','rmse.better':'Lower is better','effort.n':'Final study pending','effort.baseline':'Pending frozen final batch','effort.proposed':'Pending frozen final batch','effort.unit':'N²·m²·s','effort.better':'Lower is better','metric.name':'Final-model nominal combined demonstration (not a controller comparison)','metric.n':'1 development validation + identical recording','metric.baseline':'Not assessed in nominal development demonstration','metric.proposed':f"CLEAN_AND_HOME at {p['time_s']:.3f} s; 32/32 patches below threshold; 120 g solid retained; {100*p['coverage_metrics_v2']['qualified_contact_fraction']:.5f}% whole-panel footprint",'metric.unit':'status; s; %','metric.better':'Higher is better'},t_df_p=f"HISTORICAL only: t={stats['welch_t']:.4f}, df={stats['df']:.4f}, p={stats['p_value']:.6g}; tiny seed variance and narrow scope limit interpretation.",cohens_d=f"{stats['cohens_d_pooled']:.5f} (proposed minus baseline, historical study only)",ci95=f"[{stats['ci95_m'][0]:.8f}, {stats['ci95_m'][1]:.8f}] m, historical study only. No final-system statistical result is claimed.")
    else:
        stats=read('analytics/final_validation_v1/statistics.json');condition=next(c for c in stats['conditions'] if c['tilt_deg']==20);comparison=condition['statistics'];bc=condition['controllers']['baseline'];pc=condition['controllers']['proposed']
        put('S4',baseline_condition='Final collection model: waypoint reference + P wheel control versus segment lookahead + PI. Same camera pipeline, fixed brush/guide, mission route, guard, safety and shared incline/return regulator. Primary endpoint is common 0–30 s RMSE; all attempts continue through full mission/abort/1000 s.',n_runs='30 independent runs/controller/tilt; 10°,20°,30°; 180 full-mission attempts. All failures retained. Table below: prespecified nominal 20°; all conditions in Appendix A.',randomised='Initial x/y independent U(−0.01,+0.01) m; dust shape/offset RNG independent through logged debris_seed; clusters and 120 g lower-strip corridor fixed. Dry friction fixed. Seeds/distributions frozen before execution.',real_csv_path='analytics/final_validation_v1/tilt_{10,20,30}/{baseline,proposed}_{seed}/telemetry.csv.xz; summary.csv, protocol.json, statistics.json and trace_audit.json. A run, not a 500 Hz sample, is the unit of inference.',**{'rmse.n':f"Available 30 s windows: {bc['metrics']['primary_30s_rmse_m']['n']} baseline / {pc['metrics']['primary_30s_rmse_m']['n']} proposed; 30 attempts each",'rmse.baseline':mean_sd(bc['metrics']['primary_30s_rmse_m']),'rmse.proposed':mean_sd(pc['metrics']['primary_30s_rmse_m']),'rmse.unit':'m; common 0–30 s','rmse.better':'Lower is better','effort.n':f"Available 30 s windows: {bc['metrics']['effort_first30_Nm2_s']['n']} baseline / {pc['metrics']['effort_first30_Nm2_s']['n']} proposed; 30 attempts each",'effort.baseline':mean_sd(bc['metrics']['effort_first30_Nm2_s']),'effort.proposed':mean_sd(pc['metrics']['effort_first30_Nm2_s']),'effort.unit':'N²·m²·s; 0–30 s','effort.better':'Lower is better','metric.name':'Complete safe, camera-clean, solid-retained, serviced home cycle','metric.n':'30 per controller at 20°','metric.baseline':f"{bc['successes']}/30 ({100*bc['success_fraction']:.2f}%)",'metric.proposed':f"{pc['successes']}/30 ({100*pc['success_fraction']:.2f}%)",'metric.unit':'completion fraction','metric.better':'Higher is better'},t_df_p=f"20°: t={num(comparison.get('welch_t'),7)}, df={num(comparison.get('df'),7)}, p={num(comparison.get('p_value'),7)}; Holm-adjusted p={num(comparison.get('p_holm'),7)} across 3 tilt comparisons.",cohens_d=f"{num(comparison.get('cohens_d_pooled'),7)}; pooled SD; proposed minus baseline",ci95=f"{comparison.get('ci95_m')} m for proposed minus baseline. Run-level Welch interval; other conditions in Appendix A.")
    put('S5',linkedin_url='PENDING TEAM ACTION: post the actual team video and paste its public URL.',video_length='Source simulation: 03:20.40; final 3–4 minute team presentation with every member speaking is pending.')
    audits=[
      ('Conditional import mujoco.viewer inside mission was expected to work, but shadowed the module name and raised UnboundLocalError before model construction.','Use from mujoco import viewer as mj_viewer. Actual mission/integration tests execute model construction. See docs/AI_AUDIT.md and controller import.','Wrong code / MuJoCo API'),
      ('RMS distance to the next waypoint was initially labelled path-tracking RMSE.','Measure distance to the active segment using projection; tests/test_geometry_economics.py checks a 0.2 m perpendicular error. Time-indexed tracking is not claimed.','Wrong number or statistic'),
      ('Computing source hashes at run completion could label an earlier executed model with later edits.','Capture hashes at launch and preserve immutable source snapshots. Final batch protocol records launch hashes; executed source is frozen. See docs/AI_AUDIT.md.','Wrong code / MuJoCo API')
    ]
    for i,(said,truth,kind) in enumerate(audits,1):put('S5',**{f'ai{i}.tool':'ChatGPT',f'ai{i}.said':said,f'ai{i}.caught_by':'Ran / tested the code or simulation',f'ai{i}.truth':truth+' Development audit candidate: members must review before claiming personal verification.',f'ai{i}.error_type':kind,f'ai{i}.verdict':'Corrected'})
    return v,nominal,business,stats,business_dir

def set_control(sdt,value,pending=False):
    content=sdt.find(wt('sdtContent'));pr=sdt.find(wt('sdtPr'))
    dropdown=pr.find(wt('dropDownList'))
    if dropdown is not None and not pending:
        choices=[x.get(wt('value')) for x in dropdown]
        if value not in choices:raise ValueError((value,choices))
        dropdown.set(wt('lastValue'),value)
    for item in list(pr):
        if item.tag==wt('showingPlcHdr'):pr.remove(item)
    # Original controls are inline; preserve SDT properties, tag and choice list.
    for item in list(content):content.remove(item)
    run=E.SubElement(content,wt('r'));rp=E.SubElement(run,wt('rPr'))
    E.SubElement(rp,wt('sz')).set(wt('val'),'14')
    if pending:E.SubElement(rp,wt('highlight')).set(wt('val'),'yellow')
    text=E.SubElement(run,wt('t'));text.set('{http://www.w3.org/XML/1998/namespace}space','preserve');text.text=value

def keep_table_rows(document):
    for table in document.tables:
        for row in table.rows:
            trpr=row._tr.get_or_add_trPr()
            for height in list(trpr.findall(qn('w:trHeight'))):
                # Faculty image/code placeholders used exact heights, which clip
                # a worked example or caption after real content is inserted.
                trpr.remove(height)
            if trpr.find(qn('w:cantSplit')) is None:trpr.append(OxmlElement('w:cantSplit'))

def image_cell(cell,path,width,caption):
    cell.text='';paragraph=cell.paragraphs[0];paragraph.add_run().add_picture(str(path),width=Inches(width));r=cell.add_paragraph(caption).runs[0];r.font.size=Pt(7)

def build(preliminary=False):
    v,nominal,business,stats,business_dir=values(preliminary)
    template=ROOT/'submission/templates/MDRIIA_Group_06_Technical_Dossier_original.docx'
    out=ROOT/'docs/MDRIIA_Group_06_Technical_Dossier.docx'
    with ZipFile(template) as archive:files={i.filename:archive.read(i.filename) for i in archive.infolist()}
    xml=E.fromstring(files['word/document.xml']);controls=xml.xpath('//w:sdt',namespaces=NS);before={s.find('w:sdtPr/w:tag',NS).get(wt('val')):E.tostring(s.find('w:sdtPr',NS)) for s in controls}
    pending=[]
    for s in controls:
        tag=s.find('w:sdtPr/w:tag',NS).get(wt('val'))
        if tag in v:set_control(s,v[tag])
        else:
            pending.append(tag);set_control(s,'MEMBER TO COMPLETE' if s.find('w:sdtPr/w:dropDownList',NS) is None else 'Select ▾',True)
    files['word/document.xml']=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(out,'w',ZIP_DEFLATED) as archive:
        for name,data in files.items():archive.writestr(name,data)
    d=Document(out);tables=d.tables
    status=d.paragraphs[3].add_run('\n'+('PRELIMINARY REVIEW COPY — final validation running; team fields unsigned.' if preliminary else 'TECHNICAL REVIEW COPY — member declarations, video, peer reviews and signatures pending.'))
    status.bold=True;status.font.color.rgb=RGBColor.from_string('9C3025')
    # Correct seeded stale technical descriptions; all tagged controls remain.
    tables[6].cell(1,1).text='Group_06_Arush_Ronit_Harshvardhan/models/collection_cleaning_crawler.xml'
    tables[6].cell(3,1).text='Final model: 0.002 s, five actuators (four driven rollers approximating tracks + one rotary brush). Brush capsule contact priority 2; separate stiff solid contact; zero-friction physical containment guards. See final parameter controls below.'
    tables[6].cell(4,1).text='Monitor actual RGB → persistent dirt trigger → sweep + requested bottom-edge task → image verification/revisit → return → settle → dock service. No endless loop on a clean scene.'
    tables[6].cell(5,1).text='Rigid-body dynamics: M(q)q̈ + C(q,q̇)q̇ + g(q) = τ + Jᵀf. Ideal uphill no-slip bound: μmg cosθ ≥ mg sinθ, with Fadh=0. Wheel PI drives four roller motors; heading error creates differential wheel-speed references. Coverage is qualifying brush footprint / 24 m². Dust disappearance uses a contact-gated reduced-order removal model, not granular dust/airflow dynamics.'
    tables[8].cell(1,0).text='models/collection_cleaning_crawler.xml'
    tables[8].cell(3,0).text='analytics/final_business_model.py'
    source=(ROOT/'src/crawler_cleaning_controller.py').read_text().splitlines();start=next(i for i,line in enumerate(source) if 'for i,j in enumerate(joints):' in line)
    snippet='src/crawler_cleaning_controller.py, lines '+str(start+1)+'–'+str(start+6)+'\n'+'\n'.join(source[start:start+6])
    tables[9].cell(0,0).text=snippet
    for r in tables[9].cell(0,0).paragraphs[0].runs:r.font.name='Consolas';r.font.size=Pt(8)
    figures=ROOT/'submission/figures';figures.mkdir(exist_ok=True)
    make_fbd(figures/'free_body.png')
    image_cell(tables[10].cell(0,0),figures/'free_body.png',5.7,'Panel-tangent free-body idealisation; guard and brush contact are distinct from wheel normal load.')
    tables[10].cell(0,0).add_paragraph('m=8.5 kg, g=9.81 m/s², θ=20°: mg=83.385 N; mg sinθ=28.519 N; mg cosθ=78.355 N; ideal μmin=tan20°=0.364. No suction adhesion is simulated. These equilibrium values do not prove traction or glass safety. Actual brush normal load is brush_normal_N, guard load is guard_normal_N and panel velocities are vx/vy_panel_mps in raw CSV. Torque effort is Στ²Δt; positive mechanical work is ∫max(τq̇,0)dt. Electrical energy additionally requires declared efficiency and auxiliary-power assumptions.')
    tables[11].cell(0,1).text='Group_06_Arush_Ronit_Harshvardhan/analytics/final_business_model.py'
    tables[11].cell(1,1).text='Final operational scenario: one 24 m² tilted bay is cleaned after controlled RGB detection; manual transfer between bays is explicitly charged as human labour. No site-specific PV generation, water saving, electrical-yield recovery or commercial payback is established. The three inherited numerical claims in Section 1 are deleted.'
    tables[11].cell(2,1).text='Commercial inputs are explicitly labelled assumptions in final_business_inputs.json and varied in sensitivity.csv. Throughput/mechanical-work inputs come from the named actual simulation dataset. Modelled blower/auxiliary wattages and efficiency are assumptions; they are not electrical measurements.'
    tables[12].cell(1,1).text='Hreclaimed = H0 − [f·n·Ta/(3600p) + n·(ttransfer + (1−p)·trecovery/p)/3600 + Hmaintenance]. n=sections/month; Ta=mean attempt seconds; p=success fraction; f=supervision fraction; all transfer/recovery is human labour in the base scenario.'
    tables[12].cell(3,1).text='NCRI = 1 − κ; κ = annual robot-system cost / annual manual baseline cost. Costs are normalised to one baseline year. NCRI can be negative; payback is undefined when annual savings ≤ 0.'
    d.paragraphs[18].text='Audit correction: inherited 16–16.8% soiling and 15.2–16.2% restoration constants are excluded from the final analysis; there is no PV electrical model.'
    image_cell(tables[15].cell(0,0),ROOT/business_dir/'business_sensitivity.png',3.15,'Dimensionless commercial assumptions; no observed cost-saving claim.')
    image_cell(tables[15].cell(0,1),ROOT/business_dir/'queue_and_labour.png',3.15,'Queue distribution assumed; transfer and maintenance count as human labour.')
    tables[16].cell(0,1).text='Revised evaluation: N=30/controller/tilt at 10°,20°,30° (180 full attempts), initial pose/soil-layout variation, complete-cycle success, footprint, motion/load, simulated mechanical work. Primary controller comparison: common first-30-second tracking RMSE. PV electrical restoration and measured electrical Wh/m² are not available.'
    if preliminary:
        image_cell(tables[20].cell(0,0),ROOT/'docs/validation/collection_demo_v6/collection_evidence.png',3.15,'One completed nominal final-model demonstration; not Monte Carlo evidence.')
        image_cell(tables[20].cell(0,1),ROOT/'docs/validation/tracking_comparison.png',3.15,'HISTORICAL 30-second earlier-model comparison; kept separate from pending final batch.')
    else:
        image_cell(tables[20].cell(0,0),ROOT/'analytics/final_validation_v1/figures/representative_trajectories.png',3.15,'Prespecified first seeds at 20°; raw logs retained at 500 Hz.')
        image_cell(tables[20].cell(0,1),ROOT/'analytics/final_validation_v1/figures/tracking_and_effort.png',3.15,'All final conditions; 30 independent attempts per controller/tilt.')
    # Signatures are not SDTs. Keep them explicitly pending.
    for row in (1,2,3):
        tables[28].cell(row,4).text='SIGN PERSONALLY'
        for run in tables[28].cell(row,4).paragraphs[0].runs:run.font.highlight_color=7
    # Additions follow the preserved faculty sections.
    d.add_page_break();d.add_heading('Appendix A · Evidence scope and final evaluation',level=1)
    notice='PRELIMINARY REVIEW COPY — frozen final validation is still running. Historical tracking data and nominal development evidence are labelled separately. Replace this copy after the final batch and business recalibration finish.' if preliminary else 'Technical sections populated from the completed frozen validation and reproducible business scenario. Yellow controls, team video, peer reviews and signatures still require actual member input. This is not a signed faculty submission.'
    d.add_paragraph(notice)
    p=nominal['physical_mission'];solid=nominal['physical_solid'];inv=nominal['collection']
    d.add_paragraph(f"Validated development movie (not independent statistical replication): CLEAN_AND_HOME at {p['time_s']:.3f} simulated seconds; 32/32 selected irregular deposits below the residual threshold; qualifying whole-panel footprint {100*p['coverage_metrics_v2']['qualified_contact_fraction']:.5f}% (the exact-90% flag is false). Maximum rise above initial normal height 0.408684 mm; maximum tilt {p['maximum_chassis_tilt_deg']:.6f}°. Physical 120 g block leaves glass and is retained by the permanent tray. Initial dust inventory 4 g; final station {inv['station_waste_kg']*1000:.6f} g; residual glass {inv['remaining_on_glass_kg']*1e6:.4f} mg; mass balance error {inv['mass_balance_error_kg']:.3g} kg. Final recording and headless nominal telemetry match exactly.")
    if not preliminary:
        table=d.add_table(rows=1,cols=6);table.style='Table Grid'
        for c,text in zip(table.rows[0].cells,['Tilt','Controller','Complete cycles','0–30 s RMSE mean ± SD (m)','Coverage mean (%)','Observed duration mean (s)']):c.text=text
        for condition in stats['conditions']:
            for variant,c in condition['controllers'].items():
                row=table.add_row().cells
                for cell,text in zip(row,[str(condition['tilt_deg'])+'°',variant,f"{c['successes']}/{c['attempted']}",mean_sd(c['metrics']['primary_30s_rmse_m']),num(100*c['metrics']['coverage_fraction']['mean'],6),num(c['metrics']['duration_s']['mean'],6)]):cell.text=text
            s=condition['statistics'];d.add_paragraph(f"{condition['tilt_deg']}°: proposed−baseline Δ={num(s.get('mean_difference_m'),7)} m; 95% CI {s.get('ci95_m')}; Welch t={num(s.get('welch_t'),7)}, df={num(s.get('df'),7)}, p={num(s.get('p_value'),7)}, Holm p={num(s.get('p_holm'),7)}, Cohen d={num(s.get('cohens_d_pooled'),7)}. Completion Fisher p={num(condition['completion_fisher']['p_two_sided'],5)}.")
        d.add_paragraph('Full-run observed RMSE, effort and duration have differing exposure when a run aborts or times out; they are secondary descriptive metrics. All attempts, statuses, independent seeds, raw data and source snapshots are retained. Completion Wilson intervals and raw-trace audits are in statistics.json/trace_audit.json. No controller is declared superior solely because its mean is smaller; use the reported test and scope.')
        d.add_picture(str(ROOT/'analytics/final_validation_v1/figures/completion_and_coverage.png'),width=Inches(6.5))
    d.add_heading('Engineering limitations and interpretation',level=2)
    d.add_paragraph('Real RGB images drive contamination detection, persistence, targeted slowdowns/revisits and the departure decision. Navigation uses simulator ground-truth pose. Controlled colour/lighting segmentation is not a trained general debris detector. Two actual overhead sensor cameras and the onboard camera have visible equipment representations; scenery is isolated from validated sensor RGB. Clean/subthreshold development tests remain at home. General coloured/wet/shadowed dirt and arbitrary solid collection are unvalidated.')
    d.add_paragraph('Dust removal is a contact-gated exponential layer/mass proxy, transferred to a modelled onboard bin and then station; there is no CFD vacuum or granular dust transport. The larger block has actual gravity/collision pushing, but its release corridor is prescribed. Four driven rollers approximate tracks. Zero-friction physical guards provide containment; they are not proof of real-world grip or safe operation on an unguarded panel. Soft contact permits small penetration. Scratch, wear, motor, battery, structural mounting and electrical charging safety require hardware tests. The modelled 30 W dock service credits energy over eight seconds; it is not a demonstrated full recharge.')
    d.add_paragraph('FMEA scores are ordinal engineering judgements, not fitted failure rates. Severity and occurrence stay unchanged; any post-RPN reduction credits only the specified code/logged evaluation detection. No reduction is credited to untested coating protection. The business case assumes one cleaner repeatedly services separately transferred 24 m² bays. 504 m²/day is a workload scenario, not an inferred 100 kWp plant. Energy efficiency/auxiliary loads are assumptions; PV electrical yield is neither simulated nor monetised.')
    d.add_heading('Appendix B · References and source verification',level=1)
    d.add_paragraph('The five entries below have bibliographic metadata verified in official or author-maintained software repositories. This does not imply access to all full articles or verification of a numerical PV-loss claim. The original authorised title is preserved as a question; its 15–18% phrase is not established by this work. See submission/source_audit/source_access.json for pinned commits, hashes and access scope.')
    for citation,scope in REFERENCES:d.add_paragraph(citation+' '+scope)
    d.add_paragraph('MuJoCo developer documentation (official source, pinned in source_access.json): contact friction coefficients, geom priority and solref/solimp interpretation. IEC 61215/61730 licensed clauses were not accessed; no invented clause or certified glass-load limit is used. Historical literature scaffolds and SIMULATED_* starter outputs are excluded from final evidence.')
    d.add_heading('Appendix C · Reproduction and remaining team actions',level=1)
    d.add_paragraph('From the group directory, use the pinned Python environment in requirements.txt. Headless execution requires MUJOCO_GL=egl before importing MuJoCo. Commands and archive manifest: submission/REPRODUCE.md. Final raw files are CSV text compressed with XZ; Python pandas.read_csv reads them directly. Original field tags/choices are preserved in this Word file; edit controls in desktop Word, not Google Docs. Historical tracking CSVs use .csv.gz compression.')
    d.add_paragraph('Team: review all technical claims and code; fill genuine authorship, individual hours/learning/AI declarations and optional research consent; complete actual Group 07/12 peer reviews; record and post a 3–4 minute team presentation with all three speaking/webcam, simulation and business graph; insert its URL; each member signs personally; export the matching final PDF. Commit Word/PDF to the faculty group docs folder and every member turns in the PDF on Teams. Deadline: 26-Oct-2026, 23:59 IST.')
    keep_table_rows(d);d.save(out)
    with ZipFile(out) as archive:after=E.fromstring(archive.read('word/document.xml'))
    tags=after.xpath('//w:sdtPr/w:tag/@w:val',namespaces=NS)
    assert len(tags)==212 and set(tags)==set(before),'Faculty controls lost'
    for s in after.xpath('//w:sdt',namespaces=NS):
        tag=s.find('w:sdtPr/w:tag',NS).get(wt('val'));original=E.fromstring(before[tag]);current=s.find(wt('sdtPr'))
        oldchoices=[(i.get(wt('value')),i.get(wt('displayText'))) for i in original.findall('w:dropDownList/w:listItem',NS)]
        newchoices=[(i.get(wt('value')),i.get(wt('displayText'))) for i in current.findall('w:dropDownList/w:listItem',NS)]
        assert oldchoices==newchoices,tag
    audit={'preliminary':preliminary,'template':str(template.relative_to(ROOT)),'template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'controls_original':len(before),'controls_preserved':len(tags),'technical_fields_populated':len(v),'human_fields_pending':pending,'dossier_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
    (ROOT/'submission/dossier_field_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({'word':str(out),'controls':len(tags),'human_fields_pending':len(pending),'preliminary':preliminary},indent=2))
    return out

def make_fbd(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,2.3),constrained_layout=True)
    ax.plot([-3,3],[-.7,.7],color='#546775',lw=5);ax.plot([-.6,.5],[-.01,.245],lw=24,color='#168489')
    def arrow(x,y,dx,dy,label,color):
        ax.annotate('',xy=(x+dx,y+dy),xytext=(x,y),arrowprops=dict(arrowstyle='->',lw=1.8,color=color));ax.text(x+dx+.07,y+dy,label,color=color,fontsize=9)
    arrow(0,.45,0,-1.15,'mg','#b27032');arrow(0,.45,-.21,.90,'N (wheel support)','#3c657b');arrow(0,.45,.85,.20,'F traction','#168489')
    arrow(0,.45,-.85,-.20,'mg sin θ','#b27032');ax.text(1.6,-.35,'θ = 20°\nFadh = 0',fontsize=10);ax.text(-2.8,.75,'Brush and guard loads logged separately',fontsize=9)
    ax.set(xlim=(-3.1,3.1),ylim=(-.85,1.6),aspect='equal');ax.axis('off');fig.savefig(path,dpi=240);plt.close(fig)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preliminary',action='store_true');args=parser.parse_args();build(args.preliminary)
