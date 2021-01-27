metadata = {
    'apiLevel': '2.5',
    'protocolName': 'TG Nextera XT index kit-Step 1',
    'author': 'Lachlan Munro',
    'source': 'Custom Protocol Request'
}

#Set number of samples (Note that protocol will run full columns)

nsamples = 15
from math import ceil

def run(ctx):

    thermocycler = ctx.load_module('thermocycler')
    thermocycler.open_lid()
    thermocycler_plate = thermocycler.load_labware(
        'nest_96_wellplate_100ul_pcr_full_skirt')

    temp_deck = ctx.load_module(
        'temperature module gen2',
        '1')
    temp_rack = temp_deck.load_labware(
        'opentrons_24_aluminumblock_generic_2ml_screwcap')
    temp_deck.set_temperature(4)
    phusion_mm = temp_rack.wells_by_name()["A1"]

    DNA_plate = ctx.load_labware(
        'nest_96_wellplate_100ul_pcr_full_skirt', '3')

    mag_deck = ctx.load_module('magnetic module gen2', '4')
    mag_deck.disengage()
    mag_plate = mag_deck.load_labware(
        'nest_96_wellplate_100ul_pcr_full_skirt')

    reservoir = ctx.load_labware('nest_12_reservoir_15ml', '5')
    beads = reservoir.wells_by_name()["A1"]
    h2o = reservoir.wells_by_name()["A2"]
    etoh_list = [reservoir.wells_by_name()[x]
                 for x in ["A3", "A4", "A5", "A6"]]
    liquid_trash_list = [reservoir.wells_by_name()[x]
                         for x in ["A7", "A8", "A9", "A10", "A11"]]

    # Ethanol and Liquid trash simulation
    class ReservoirMaterial():
        def __init__(self, lanes):
            self.lanes = lanes
        liquid_taken = 0
        depth_per_lane = 14800
        current_lane = 0

        def get_lane(self, liquid_quantity):
            if liquid_quantity + self.liquid_taken > self.depth_per_lane:
                self.current_lane += 1
                self.liquid_taken = 0
            self.liquid_taken += liquid_quantity
            return self.lanes[self.current_lane]

    etoh = ReservoirMaterial(etoh_list)
    liquid_trash = ReservoirMaterial(liquid_trash_list)


    t1 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 6)
    t2 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 9)
    t3 = ctx.load_labware("opentrons_96_filtertiprack_20ul", 2)


    p300m = ctx.load_instrument(
        "p300_multi_gen2",
        "left",
        tip_racks=[t1, t2])

    p20m = ctx.load_instrument(
    	"p20_multi_gen2", 
    	"right",
    	tip_racks=[t3])



    #Use multi channel as a single channel to dispense master mix into all wells in PCR plate.
    #Note that tip in H12 will be reused, so may have trace Master mix.

    nCols = ceil(nsamples/8)

    p300m.pick_up_tip(t1["H12"])
    for col in range(nCols):
    	p300m.aspirate(175, phusion_mm)
    	for w in range(8):
    		p300m.dispense(21, thermocycler_plate.wells()[col*8 + w])
    		p300m.touch_tip()
    		p300m.blow_out(phusion_mm)
    p300m.blow_out(phusion_mm)
    p300m.return_tip()

    #Transfer from DNA plate
    DNACols = DNA_plate.columns()[0:nCols]
    thermoCols = thermocycler_plate.columns()[0:nCols]
    p20m.transfer(2, DNACols, thermoCols, new_tip="always", mix_after=(2, 20), touch_tip=True)

    #Function to define touchdown PCR cycle
    def stp(temp, hold):
        return {"temperature": temp, "hold_time_seconds": hold}
    steps = []
    steps.append(stp(98, 300))
    steps += [item for sublist in [[stp(98, 10), stp(69 - x, 10), stp(72, 30)]
                                   for x in range(0, 10)] for item in sublist]
    steps += [item for sublist in [[stp(98, 10), stp(72, 30)]
                                   for _ in range(0, 25)] for item in sublist]
    steps.append(stp(72, 420))
    steps.append(stp(10, 10))

    thermocycler.close_lid()
    thermocycler.set_lid_temperature(99)
    thermocycler.execute_profile(
        steps=steps,
        repetitions=1, block_max_volume=25)
    thermocycler.open_lid()

    ctx.pause("Move plate from thermocycler to mag_deck. Replace DNA plate on slot 3 with fresh PCR Plate")

    #Mix neccesary? 
    mag_cols = mag_plate.columns()[0:nCols]
    for col in mag_cols:
    	p300m.transfer(45, beads, col, mix_before=(3, 150), mix_after=(3, 50), new_tip="always")

    ctx.delay(30)
    mag_deck.engage()
    ctx.delay(600)

    def load_eth(src, dst):
    	p300m.transfer(150, src, dst.top(), new_tip="never")

    p300m.pick_up_tip()

    for col in mag_cols:
    	load_eth(etoh.get_lane(150), col[0])

    p300m.return_tip()

    ctx.delay(30)

    for col in mag_cols:
    	p300m.transfer(150, col, liquid_trash.get_lane(150), touch_tip=True, trash=False, return_tips=True)

    for col in mag_cols:
    	p300m.transfer(150, col, liquid_trash.get_lane(150), touch_tip=True, trash=False, return_tips=True)





