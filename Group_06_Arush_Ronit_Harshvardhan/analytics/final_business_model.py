"""Measured-throughput, dimensionless scenario economics; never claims sourced commercial savings."""
from pathlib import Path
import argparse,copy,json,math
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def calculate(inputs,measured):
    cfg=inputs
    if cfg['manual_person_hours_per_month']<=0 or cfg['life_years']<=0 or not 0<cfg['electromechanical_efficiency']<=1 or not 0<=cfg['supervision_fraction']<=1:raise ValueError('Invalid economic inputs')
    p=float(measured['success_fraction']);attempt=float(measured['mean_attempt_s'])
    if not 0<=p<=1 or attempt<=0:raise ValueError('Invalid measured success/time')
    if p==0:
        unavailable={key:None for key in ('service_mean_s','queue_wait_h','queue_system_h','robot_operating_h_month','supervision_person_h_month','transfer_recovery_person_h_month','total_robot_related_person_h_month','labour_reclaimed_person_h_month','estimated_robot_Wh_per_successful_section','estimated_system_kWh_year','labour_cost_ratio','energy_cost_ratio','nonlabour_cost_ratio','kappa','NCRI','payback_months','lifetime_normalised_payback','break_even_supervision_fraction','estimated_energy_Wh_per_modelled_m2')}
        return {**unavailable,'viable_service':False,'success_fraction':p,'mean_attempt_s':attempt,'arrival_rate_sections_h':cfg['sections_per_day']/cfg['operating_hours_per_day'],'servers':1,'service_rate_sections_h':0.,'queue_stable':False,'utilisation':None,'maximum_capital_ratio_for_payback_within_life':0.}
    # Renewal calculation: E[T_success]=(E[T_attempt]+(1-p)*recovery)/p.
    recovery=(1-p)*cfg['failed_attempt_recovery_s']/p
    service=attempt/p+recovery+cfg['between_section_transfer_s'];mu=3600/service
    arrivals=cfg['sections_per_day']/cfg['operating_hours_per_day'];rho=arrivals/mu
    robot_hours=cfg['sections_per_day']*cfg['operating_days_per_month']*service/3600
    tasks=cfg['sections_per_day']*cfg['operating_days_per_month']
    active_robot_hours=tasks*attempt/p/3600
    supervision=cfg['supervision_fraction']*active_robot_hours
    transfer_recovery=tasks*(cfg['between_section_transfer_s']*cfg['between_section_transfer_human_fraction']+recovery*cfg['failed_attempt_recovery_human_fraction'])/3600
    human_hours=supervision+transfer_recovery+cfg['maintenance_person_hours_per_month']
    attempt_robot_Wh=(measured['mean_positive_mechanical_work_J']/cfg['electromechanical_efficiency']+measured['mean_modelled_blower_J']+cfg['robot_electronics_W']*attempt)/3600
    robot_Wh=attempt_robot_Wh/p+cfg['robot_electronics_W']*(recovery+cfg['between_section_transfer_s'])/3600
    annual_energy=(cfg['sections_per_day']*robot_Wh+cfg['external_camera_count']*cfg['external_camera_W_each']*cfg['operating_hours_per_day'])*cfg['operating_days_per_month']*12/1000
    labour_ratio=human_hours/cfg['manual_person_hours_per_month']
    energy_ratio=annual_energy*cfg['electricity_cost_per_kWh_to_one_year_manual_cost_ratio']
    nonlabour=energy_ratio+cfg['battery_and_spares_annual_cost_ratio']+cfg['consumables_annual_cost_ratio']
    kappa=labour_ratio+nonlabour;ncri=1-kappa;k=cfg['capital_to_one_year_manual_cost_ratio']
    return {'viable_service':True,'success_fraction':p,'mean_attempt_s':attempt,'service_mean_s':service,'service_rate_sections_h':mu,'arrival_rate_sections_h':arrivals,'servers':1,'queue_model':'M/M/1 distribution assumptions; empirical mean service capacity','utilisation':rho,'queue_stable':rho<1,'queue_wait_h':arrivals/(mu*(mu-arrivals)) if rho<1 else None,'queue_system_h':1/(mu-arrivals) if rho<1 else None,'robot_operating_h_month':robot_hours,'supervision_person_h_month':supervision,'transfer_recovery_person_h_month':transfer_recovery,'total_robot_related_person_h_month':human_hours,'labour_reclaimed_person_h_month':cfg['manual_person_hours_per_month']-human_hours,'estimated_robot_Wh_per_successful_section':robot_Wh,'estimated_system_kWh_year':annual_energy,'labour_cost_ratio':labour_ratio,'energy_cost_ratio':energy_ratio,'nonlabour_cost_ratio':nonlabour,'kappa':kappa,'NCRI':ncri,'payback_months':12*k/ncri if ncri>0 else None,'lifetime_normalised_payback':k/(cfg['life_years']*ncri) if ncri>0 else None,'break_even_supervision_fraction':(cfg['manual_person_hours_per_month']*(1-nonlabour)-cfg['maintenance_person_hours_per_month']-transfer_recovery)/active_robot_hours,'maximum_capital_ratio_for_payback_within_life':cfg['life_years']*ncri if ncri>0 else 0.,'estimated_energy_Wh_per_modelled_m2':robot_Wh/cfg['section_area_m2']}


def build(validation,output,inputs_path=None,nominal=False):
    validation=Path(validation);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    inputs_path=Path(inputs_path) if inputs_path else Path(__file__).with_name('final_business_inputs.json');inputs=json.loads(inputs_path.read_text())
    if nominal:
        report=json.loads((validation/'result.json').read_text());physical=report['physical_mission']
        if report['status']!='CLEAN_AND_HOME':raise ValueError('Nominal calibration requires a completed validated mission')
        measured={'source':str(validation/'result.json'),'selection':'PROVISIONAL: one completed nominal development demonstration, not the frozen Monte Carlo study','n':1,'successes':1,'success_fraction':1.,'mean_attempt_s':physical['time_s'],'mean_positive_mechanical_work_J':physical['positive_mechanical_work_J'],'mean_modelled_blower_J':report['collection']['blower_energy_J'],'units':{'mean_attempt_s':'s','mean_positive_mechanical_work_J':'J simulated mechanical work','mean_modelled_blower_J':'J at assumed 20 W, not measured electrical power'}}
        stats=None
    else:
        protocol=json.loads((validation/'protocol.json').read_text());data=pd.read_csv(validation/'summary.csv');stats=json.loads((validation/'statistics.json').read_text())
        selected=data[(data.tilt_deg==20)&(data.variant=='proposed')];expected=protocol['runs_per_controller_per_tilt']
        if len(selected)!=expected or expected<30:raise ValueError('Requires all >=30 nominal proposed trials, including failures')
        success=selected.success.astype(str).str.lower().eq('true')
        measured={'source':str(validation/'summary.csv'),'selection':'All proposed attempts at 20 degrees; failures retained','n':len(selected),'successes':int(success.sum()),'success_fraction':float(success.mean()),'mean_attempt_s':float(selected.duration_s.mean()),'mean_positive_mechanical_work_J':float(selected.work_J.mean()),'mean_modelled_blower_J':float(selected.blower_J.mean()),'units':{'mean_attempt_s':'s','mean_positive_mechanical_work_J':'J measured from simulated actuator torque and speed','mean_modelled_blower_J':'J at assumed 20 W, not measured electrical power'}}
    result=calculate(inputs,measured)
    (output/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');(output/'simulation_inputs.json').write_text(json.dumps(measured,indent=2)+'\n')
    report={'input_status':'Dimensionless scenario assumptions with measured simulation throughput/work; not verified market costs or field energy savings','measured':measured,'base_case':result,'assumptions':inputs,'excluded_claims':['140000 kWh/year in Mumbai not independently established here','16% monthly soiling does not equal 16% annual yield loss','15.2% electrical power restoration and 8.6-month payback are not results of this simulation'],'uncertainty':'Initial pose/soil/tilt trial uncertainty and commercial scenario uncertainty are separate; no claim that N simulation trials establish field reliability.'}
    rows=[]
    varied=['supervision_fraction','manual_person_hours_per_month','capital_to_one_year_manual_cost_ratio','between_section_transfer_s','failed_attempt_recovery_s','electricity_cost_per_kWh_to_one_year_manual_cost_ratio','maintenance_person_hours_per_month','electromechanical_efficiency']
    for parameter in varied:
        for factor in (.7,1.,1.3):
            cfg=copy.deepcopy(inputs);cfg[parameter]*=factor
            if parameter in ('supervision_fraction','electromechanical_efficiency'):cfg[parameter]=min(1.,cfg[parameter])
            rows.append({'parameter':parameter,'factor':factor,'input_value':cfg[parameter],**calculate(cfg,measured)})
    if stats is not None:
        nominal_stat=next(c for c in stats['conditions'] if c['tilt_deg']==20)['controllers']['proposed']
        conservative=copy.deepcopy(measured);conservative['success_fraction']=nominal_stat['wilson95'][0]
        report['success_lower_confidence_scenario']=calculate(inputs,conservative)
    else:
        report['status']='PROVISIONAL SINGLE-RUN SCENARIO; final Monte Carlo calibration pending'
    pd.DataFrame(rows).to_csv(output/'sensitivity.csv',index=False)
    fig,axes=plt.subplots(1,2,figsize=(10.5,4),constrained_layout=True)
    fractions=np.linspace(.02,1,100);values=[]
    for fraction in fractions:
        cfg=copy.deepcopy(inputs);cfg['supervision_fraction']=float(fraction);values.append(calculate(cfg,measured))
    axes[0].plot(fractions,[v['NCRI'] for v in values],color='#168489');axes[0].axhline(0,color='#999',ls='--');axes[0].axvspan(inputs['supervision_fraction']*.7,inputs['supervision_fraction']*1.3,color='#168489',alpha=.12,label='Assumed base ±30%');axes[0].set(xlabel='Assumed supervision fraction of operating time',ylabel='Normalised cost reduction (NCRI)',title='Commercial scenario; not observed savings');axes[0].legend(fontsize=8)
    axes[1].plot(fractions,[v['payback_months'] if v['payback_months'] is not None else np.nan for v in values],color='#b27032');axes[1].set(xlabel='Assumed supervision fraction',ylabel='Simple payback (months)',ylim=(0,60),title='Undefined when annual savings ≤ 0')
    fig.savefig(output/'business_sensitivity.png',dpi=260);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10.5,4),constrained_layout=True)
    if result['service_rate_sections_h']>0:
        utilisation=np.linspace(.05,.97,100);mu=result['service_rate_sections_h'];wait=utilisation/(mu*(1-utilisation))
        axes[0].plot(utilisation,wait*60,label='M/M/1',color='#168489');axes[0].plot(utilisation,wait*30,ls='--',label='M/D/1 reference',color='#b27032');axes[0].set(xlabel='Utilisation ρ = λ/μ',ylabel='Scenario queue wait (min)',title=f'μ={mu:.3f} modelled sections/hour');axes[0].legend()
        axes[1].bar(['Manual'],[inputs['manual_person_hours_per_month']],color='#b27032',label='Manual baseline')
        bottom=0.
        for label,value,color in [('Monitoring',result['supervision_person_h_month'],'#168489'),('Transfer / recovery',result['transfer_recovery_person_h_month'],'#70a4aa'),('Maintenance',inputs['maintenance_person_hours_per_month'],'#658793')]:
            axes[1].bar(['Robot system'],[value],bottom=bottom,color=color,label=label);bottom+=value
        axes[1].set(ylabel='Assumed/derived person-hours per month',title='Labour scenario: no field observation');axes[1].legend(fontsize=7)
    fig.savefig(output/'queue_and_labour.png',dpi=260);plt.close(fig)
    (output/'results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2,allow_nan=False));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--validation-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--inputs',type=Path);p.add_argument('--nominal',action='store_true');a=p.parse_args();build(a.validation_dir,a.output_dir,a.inputs,a.nominal)
