     

   
metadata = {
    'protocolName': 'Transformation',
    'author': 'Lachlan <lajamu@biosustain.dtu.dk',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.8'
}


def run(protocol):
    
        #Load Tips
        tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', '5')
        
        #Load Pipettes
        p300Multi = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=[tips300])


        plate = protocol.load_labware("corning_96_wellplate_360ul_flat", 4)
        rack = protocol.load_labware("opentrons_24_aluminumblock_nest_1.5ml_snapcap", 6)
        water = rack["A1"]
        p300Multi.pick_up_tip(tips300["H12"])

        p300Multi.aspirate(180, water)
        for i in plate.wells()[0:8]:
            p300Multi.dispense(20, i)


        p300Multi.return_tip()
        
        




        
