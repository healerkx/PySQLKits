

from batchinsert import *


if __name__ == '__main__':
    s = RelatedDataSource('lottery_prize_pool.csv')
    i = Insert('hd_lottery_prize_pool', 
        prize_id=None,
        prize_type=s.get_generator('prize_type'),
        prize_title=s.get_generator('prize_title'),
        prize_weight=[1],
        virtual_prize_type=s.get_generator('virtual_prize_type'),
        virtual_prize_amount=s.get_generator('virtual_prize_amount'),
        display_position=s.get_generator('display_position'),
        lottery_id=[1],
        member_id=[0],
        prize_status=[0],
        status=[1],
        create_time=['2016-09-20 13:00:00'],
        last_modified=['2016-09-20 13:00:00'],
    )

    i.set_related_data_source(s)
    i.set_fields_order([
            'prize_id', 'prize_type', 'prize_title', 'prize_weight', 
            'virtual_prize_type', 'virtual_prize_amount', 'display_position', 
            'lottery_id', 'member_id', 'prize_status',
            'status', 'create_time', 'last_modified'])
            
    i.perform(None, 200000)

