"""Independent numeric fixtures for source equivalence, thresholds and isolation.

Generated only in the temporary Promtool suite; no snapshots or host changes.
"""
import json


def matrix_cases():
    suite={'evaluation_interval':'1m','tests':[]}
    base={'instance':'matrix-host','tenant':'matrix','environment':'lab','site':'test'}
    def series(name,labels,values):return {'series':name+'{'+','.join(k+'='+json.dumps(str(v)) for k,v in labels.items())+'}','values':values}
    def check(expr,time,value=None):return {'expr':expr,'eval_time':time,'exp_samples':[] if value is None else [{'labels':'{}','value':value}]}
    for collector in ['node','alloy','telegraf','windows']:
     for resource,values in [('Cpu',{'high':(35,45),'mid':(75,90),'low':(90,98)}),('Memory',{'high':(65,80),'mid':(85,92),'low':(92,97)})]:
      for level,(warn,error) in values.items():
       for severity,value in [('WARN',warn),('ERROR',error)]:
        labels=dict(base,job=collector,**{'lpm_'+('cpu' if resource=='Cpu' else 'mem')+'_criticality':level})
        inputs=[]
        if resource=='Cpu':
         if collector=='windows':inputs=[series('windows_cpu_time_total',dict(labels,core='0',mode='idle'),'0+'+str((100-value)*.6)+'x100'),series('windows_system_boot_time_timestamp',base,'-4000+0x100')]
         elif collector=='telegraf':inputs=[series('cpu_usage_idle',dict(labels,cpu='cpu-total'),str(100-value)+'+0x100'),series('system_uptime',base,'4000+0x100')]
         else:inputs=[series('node_cpu_seconds_total',dict(labels,cpu='0',mode='idle'),'0+'+str((100-value)*.6)+'x100'),series('node_boot_time_seconds',base,'-4000+0x100')]
        elif collector=='windows':inputs=[series('windows_memory_physical_free_bytes',labels,str(100-value)+'+0x100'),series('windows_memory_physical_total_bytes',labels,'100+0x100')]
        elif collector=='telegraf':inputs=[series('mem_available',labels,str(100-value)+'+0x100'),series('mem_total',labels,'100+0x100')]
        else:inputs=[series('node_memory_MemAvailable_bytes',labels,str(100-value)+'+0x100'),series('node_memory_MemTotal_bytes',labels,'100+0x100')]
        alert='LPM'+resource+level.title()+'_'+severity
        tests=[check('count(ALERTS{alertname="'+alert+'",alertstate="firing"})','10m'),check('count(ALERTS{alertname="'+alert+'",alertstate="firing"})','80m' if level=='low' else '40m',1)]
        if severity=='WARN':tests.append(check('count(ALERTS{alertname="LPM'+resource+level.title()+'_ERROR",alertstate="firing"})','80m' if level=='low' else '40m'))
        if level=='low':tests.append(check('count(ALERTS{alertname="'+alert+'",alertstate="firing"})','59m'))
        suite['tests'].append({'name':f'{collector} {resource} {level} {severity} boundary and hold','interval':'1m','input_series':inputs,'promql_expr_test':tests})
    # Counter units are deliberately different; all sources must normalize identically.
    for collector in ['node','alloy','telegraf']:
     labels=dict(base,job=collector,name='sda',lpm_io_criticality='high')
     if collector=='telegraf':mapping={'diskio_io_time':'0+54000x100','diskio_read_time':'0+1200x100','diskio_write_time':'0+1800x100','diskio_reads':'0+40x100','diskio_writes':'0+60x100','diskio_iops_in_progress':'6+0x100'}
     else:
      labels['device']=labels.pop('name');mapping={'node_disk_io_time_seconds_total':'0+54x100','node_disk_read_time_seconds_total':'0+1.2x100','node_disk_write_time_seconds_total':'0+1.8x100','node_disk_reads_completed_total':'0+40x100','node_disk_writes_completed_total':'0+60x100','node_disk_io_now':'6+0x100'}
     inputs=[series(k,labels,v) for k,v in mapping.items()]+[series('system_uptime' if collector=='telegraf' else 'node_boot_time_seconds',base,'4000+0x100' if collector=='telegraf' else '-4000+0x100')]
     tests=[check('count(abs(lpm:diskio_utilization:avg15m - 0.9) < 0.000001)','40m',1),check('count(abs(lpm:diskio_await:avg15m - 30) < 0.000001)','40m',1),check('count(lpm:diskio_queue:avg15m == 6)','40m',1),check('count(ALERTS{alertname="LPMDiskIOUtilHigh_ERROR",alertstate="firing"})','40m',1)]
     suite['tests'].append({'name':collector+' IO units and alarm','interval':'1m','input_series':inputs,'promql_expr_test':tests})
    # Current presence and namespace isolation must expire old aliases without merging mounts.
    inputs=[]
    for path,values in [('/data','95+0x60'),('/alias','95+0x20 stale')]:
     labels=dict(base,path=path,device='vda1',fstype='ext4')
     inputs.extend([series('disk_used_percent',labels,values),series('disk_total',labels,'100+0x60' if path=='/data' else '100+0x20 stale'),series('disk_inodes_used',labels,values),series('disk_inodes_total',labels,'100+0x60' if path=='/data' else '100+0x20 stale')])
    labels=dict(base,path='/alias',device='vda1',fstype='ext4',tenant='other')
    inputs.extend([series('disk_used_percent',labels,'95+0x60'),series('disk_total',labels,'100+0x60')])
    suite['tests'].append({'name':'telegraf current mount and tenant isolation','interval':'1m','input_series':inputs,'promql_expr_test':[check('count(lpm:disk_used_percent:avg15m{tenant="matrix",path="/alias"})','30m'),check('count(lpm:disk_inodes_used_percent:avg15m{tenant="matrix",path="/alias"})','30m'),check('count(lpm:disk_used_percent:avg15m{tenant="matrix",path="/data"})','30m',1),check('count(lpm:disk_used_percent:avg15m{tenant="other",path="/alias"})','30m',1)]})
    # Zero totals must not become Inf/NaN recordings or alarms.
    inputs=[series(k,base,v) for k,v in {'mem_available':'0+0x60','mem_total':'0+0x60','swap_free':'0+0x60','swap_total':'0+0x60','conntrack_ip_conntrack_count':'0+0x60','conntrack_ip_conntrack_max':'0+0x60'}.items()]
    labels=dict(base,path='/zero',device='vda',fstype='ext4');inputs.extend(series(k,labels,v) for k,v in {'disk_used_percent':'100+0x60','disk_total':'0+0x60','disk_inodes_used':'0+0x60','disk_inodes_total':'0+0x60'}.items())
    suite['tests'].append({'name':'telegraf zero denominators','interval':'1m','input_series':inputs,'promql_expr_test':[check(name,'30m') for name in ['lpm:mem_utilization:avg15m','lpm:swap_utilization:avg15m','lpm:conntrack_utilization','lpm:disk_used_percent:avg15m','lpm:disk_inodes_used_percent:avg15m','ALERTS']]})
    # Avoid duplicate output series when a sender accidentally exposes both families.
    labels=dict(base,path='/data',device='/dev/vda',mountpoint='/data',fstype='ext4');tg=dict(base,path='/data',device='vda',fstype='ext4')
    suite['tests'].append({'name':'node family takes precedence over telegraf for same identity and mount','interval':'1m','input_series':[series('node_filesystem_avail_bytes',labels,'80+0x60'),series('node_filesystem_size_bytes',labels,'100+0x60'),series('disk_used_percent',tg,'95+0x60'),series('disk_total',tg,'100+0x60')],'promql_expr_test':[check('count(lpm:disk_used_percent:avg15m)','30m',1),check('count(lpm:disk_used_percent:avg15m > 90)','30m')]})
    # Services must be explicitly expected; unrelated stopped units do not alert.
    for collector in ['node','alloy','telegraf','windows']:
     labels=dict(base,name='selected.service',lpm_service_expected='true',lpm_systemd_criticality='high')
     if collector=='telegraf':metric='systemd_units_active_code';value='3+0x10'
     elif collector=='windows':metric='windows_service_state';labels['state']='running';value='0+0x10'
     else:metric='node_systemd_unit_state';labels['state']='active';value='0+0x10'
     unselected=dict(labels,name='unselected.service');unselected.pop('lpm_service_expected')
     suite['tests'].append({'name':collector+' expected-service selection','interval':'1m','input_series':[series(metric,labels,value),series(metric,unselected,value)],'promql_expr_test':[check('count(ALERTS{alertname="LPMSystemdServiceHigh_ERROR",alertstate="firing"})','3m',1),check('count(ALERTS{name="unselected.service"})','3m')]})
    for kind,metric in [('port','net_response_result_code'),('http','http_response_result_code')]:
     for source in ['telegraf','blackbox']:
      labels=dict(base,monitoring_profile='lpm',platform='linux',lpm_portcheck_criticality='high')
      if source=='telegraf':labels.update(server='service.invalid',port='1234',protocol='tcp',method='GET');name=metric;value='3+0x10'
      else:labels.update(instance='service.invalid:1234',probe_kind=kind);name='probe_success';value='0+0x10'
      suite['tests'].append({'name':source+' '+kind+' explicit check alarm','interval':'1m','input_series':[series(name,labels,value)],'promql_expr_test':[check('count(ALERTS{alertname="LPM'+('Port' if kind=='port' else 'Http')+'checkHigh_ERROR",alertstate="firing"})','3m',1)]})

    for source in ['node','alloy','telegraf']:
     for category,classes in [('DiskUsage',{'high':(75,90),'mid':(85,95),'low':(92,97)}),('ConntrackUtil',{'high':(.55,.75),'mid':(.75,.90),'low':(.90,.98)})]:
      for level,pair in classes.items():
       for severity,value in zip(['WARN','ERROR'],pair):
        labels=dict(base,job=source,**{'lpm_'+('dsk' if category=='DiskUsage' else 'conntrack')+'_criticality':level})
        if category=='DiskUsage':
         labels.update(device='vda',fstype='ext4')
         if source=='telegraf':labels['path']='/data';inputs=[series('disk_used_percent',labels,f'{value}+0x100'),series('disk_total',labels,'100+0x100')]
         else:labels['mountpoint']='/data';inputs=[series('node_filesystem_avail_bytes',labels,f'{100-value}+0x100'),series('node_filesystem_size_bytes',labels,'100+0x100')]
        else:
         prefix='conntrack_ip_conntrack_' if source=='telegraf' else 'node_nf_conntrack_entries';inputs=[series(prefix+('count' if source=='telegraf' else ''),labels,f'{round(value*1000)}+0x100'),series(prefix+('max' if source=='telegraf' else '_limit'),labels,'1000+0x100')]
        name='LPM'+category+level.title()+'_'+severity;late='80m' if level=='low' and category=='DiskUsage' else '40m'
        tests=[check('count(ALERTS{alertname="'+name+'",alertstate="firing"})','2m'),check('count(ALERTS{alertname="'+name+'",alertstate="firing"})',late,1)]
        if severity=='WARN':tests.append(check('count(ALERTS{alertname="LPM'+category+level.title()+'_ERROR",alertstate="firing"})',late))
        suite['tests'].append({'name':f'{source} {category} {level} {severity} threshold','interval':'1m','input_series':inputs,'promql_expr_test':tests})
     for level,severity,rate in [('high','WARN',.5),('high','ERROR',2),('mid','WARN',2),('mid','ERROR',6),('low','ERROR',21)]:
      labels=dict(base,job=source,lpm_neterr_criticality=level)
      if source=='telegraf':labels['interface']='eth0';metric='net_err_in'
      else:labels['device']='eth0';metric='node_network_receive_errs_total'
      name='LPMNetErrIn'+level.title()+'_'+severity
      suite['tests'].append({'name':f'{source} network {level} {severity} rate','interval':'1m','input_series':[series(metric,labels,f'0+{rate*60}x60')],'promql_expr_test':[check('count(ALERTS{alertname="'+name+'",alertstate="firing"})','2m'),check('count(ALERTS{alertname="'+name+'",alertstate="firing",interface="eth0"})','40m',1)]})
     metric='kernel_vmstat_oom_kill' if source=='telegraf' else 'node_vmstat_oom_kill'
     suite['tests'].append({'name':source+' actual OOM counter event and expiry','interval':'1m','input_series':[series(metric,base,'0+0x4 1+0x20')],'promql_expr_test':[check('count(ALERTS{alertname="LPMMemoryOOMKilled_ERROR",alertstate="firing"})','0m'),check('count(ALERTS{alertname="LPMMemoryOOMKilled_ERROR",alertstate="firing"})','5m',1),check('count(ALERTS{alertname="LPMMemoryOOMKilled_ERROR",alertstate="firing"})','11m')]})
    # Available memory, rather than an incompatible used-percent field, controls cache-aware pressure.
    suite['tests'].append({'name':'telegraf reclaimable cache is not memory exhaustion','interval':'1m','input_series':[series(k,base,v) for k,v in {'mem_available':'60+0x60','mem_total':'100+0x60','mem_free':'1+0x60','mem_used_percent':'99+0x60'}.items()],'promql_expr_test':[check('count(lpm:mem_utilization:avg15m == 40)','40m',1),check('ALERTS','40m')]})
    labels=dict(base,interface='eth0')
    suite['tests'].append({'name':'telegraf network counter resets keep byte-per-second units','interval':'1m','input_series':[series('net_bytes_recv',labels,'0+6000x20 0+6000x40')],'promql_expr_test':[check('count(abs(lpm:net_bytes_recv:rate5m - 100) < 0.000001)','40m',1)]})

    # OOM is deliberately kept firing for 15 minutes after its five-minute event window.
    for case in suite['tests']:
     if 'actual OOM counter event and expiry' in case['name']:
      case['promql_expr_test'][-1]['exp_samples']=[{'labels':'{}','value':1}]
      case['promql_expr_test'].append(check('count(ALERTS{alertname="LPMMemoryOOMKilled_ERROR",alertstate="firing"})','30m'))
    # Endpoint identity supplied by an operator must survive blackbox normalization.
    labels=dict(base,target='service.invalid:1234',probe_kind='port',monitoring_profile='lpm',lpm_portcheck_criticality='high')
    suite['tests'].append({'name':'blackbox explicit endpoint identity is preserved','interval':'1m','input_series':[series('probe_success',labels,'0+0x10')],'promql_expr_test':[check('count(lpm:portcheck_result_code{target="service.invalid:1234"})','3m',1)]})
    # Windows exporter counters use seconds, while the normalized latency is milliseconds.
    labels = dict(base, volume='C:', lpm_io_criticality='high')
    mapping = {'windows_logical_disk_idle_seconds_total': '0+6x100',
               'windows_logical_disk_read_seconds_total': '0+1.2x100',
               'windows_logical_disk_write_seconds_total': '0+1.8x100',
               'windows_logical_disk_reads_total': '0+40x100',
               'windows_logical_disk_writes_total': '0+60x100',
               'windows_logical_disk_requests_queued': '6+0x100'}
    inputs = [series(name, labels, values) for name, values in mapping.items()]
    inputs.append(series('windows_system_boot_time_timestamp', base, '-4000+0x100'))
    suite['tests'].append({'name': 'alloy Windows IO units and alarms', 'interval': '1m',
                          'input_series': inputs, 'promql_expr_test': [
                              check('count(abs(lpm:diskio_utilization:avg15m - 0.9) < 0.000001)', '40m', 1),
                              check('count(abs(lpm:diskio_await:avg15m - 30) < 0.000001)', '40m', 1),
                              check('count(ALERTS{alertname="LPMDiskIOUtilHigh_ERROR",alertstate="firing"})', '40m', 1)]})
    return suite['tests']
