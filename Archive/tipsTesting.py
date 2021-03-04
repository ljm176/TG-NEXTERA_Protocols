     

   
metadata = {
    'protocolName': 'Transformation',
    'author': 'Lachlan <lajamu@biosustain.dtu.dk',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.8'
}


def run(protocol):
    
        #Load Tips
        tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', '5')
        
        #Load Pipettes
        p20Multi = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=[tips20])


        plate = protocol.load_labware("corning_96_wellplate_360ul_flat", 4)
        rack = protocol.load_labware("opentrons_24_aluminumblock_nest_1.5ml_snapcap", 6)
        water = rack["A1"]
        
        p20Multi.pick_up_tip(tips20.wells()[95])
        p20Multi.drop_tip()
        p20Multi.pick_up_tip(tips20.wells()[94].top(10))
        p20Multi.drop_tip()
        p20Multi.pick_up_tip(tips20.wells()[93].top(5))
        p20Multi.drop_tip()




        
