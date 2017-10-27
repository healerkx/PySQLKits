
from batchinsert import *


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Please provide an output filename")
        exit()

    app_id_converter = lambda x : x + 1
    
    i = Insert('st_store_app_statistics_daily', 
        statistics_id=None,
        statistics_type=[0],
        statistics_time=IntegerRange(begin=unixtime('2017-03-01'), end=unixtime('2017-04-01'), step=86400, repeat_times=20, order='asc'),
        app_id=DependentValue(reletive_row_index=-1, init_value=2, converter=app_id_converter),
        app_type=[0],

        store_count_new=[0, 1],
        store_count_total=[1, 2],
        active_store_count=[1, 2],
        active_store_count_avg30=[1, 2],
        launch_count=[1, 2],
        launch_count_avg30=[1, 2],
        download_count=[1, 2],
        download_count_total=[1, 2],
        
        status=[1],
        create_time=[1488297600],
        update_time=[1488297600],
    )

    i.set_fields_order([
        'statistics_id', 'statistics_type', 'statistics_time', 
        'app_id', 
        'app_type', 
        'store_count_new', 'store_count_total', 
        'active_store_count', 'active_store_count_avg30', 
        'launch_count', 'launch_count_avg30', 
        'download_count', 'download_count_total', 
        'status', 'create_time', 'update_time'])

    filename = sys.argv[1]
    i.perform(100, filename, 'insert')


