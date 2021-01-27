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

    DNA_plate = ctx.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '3')

    primer_plate = ctx.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '4')
    

    t1 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 6)
    t2 = ctx.load_labware("opentrons_96_filtertiprack_20ul", 9)
    t3 = ctx.load_labware("opentrons_96_filtertiprack_20ul", 2)


    p300s = ctx.load_instrument(
        "p300_single",
        "left",
        tip_racks=[t1])

    p20m = ctx.load_instrument(
    	"p20_multi_gen2", 
    	"right",
    	tip_racks=[t2, t3])



    #add master mix to wells
    p300s.distribute(21, phusion_mm, thermocycler_plate.wells()[0:nsamples])


    nCols = ceil(nsamples/8)
    #Transfer from DNA plate
    DNACols = DNA_plate.columns()[0:nCols]
    thermoCols = thermocycler_plate.columns()[0:nCols]
    primerCols = primer_plate.columns()[0:nCols]

    p20m.transfer(2, primerCols, thermoCols, new_tip="always", touch_tip=True, mix_after=(1, 10))
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

