metadata = {
    'apiLevel': '2.5',
    'protocolName': 'TG Nextera XT index kit-Step 1',
    'author': 'Lachlan Munro (lajamu@biosustain.dtu.dk',
}

#Parts of protocol modified from Opentrons protocol library


#Set number of samples (Note that protocol will run full columns)

nsamples = 96
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
    kappa_mm = temp_rack.wells_by_name()["A1"]

    DNA_plate = ctx.load_labware(
        'nest_96_wellplate_100ul_pcr_full_skirt', '3')

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
    	tip_racks=[t3])

    nCols = ceil(nsamples/8)

    #add master mix to wells
    p300s.pick_up_tip()
    for c in range(nCols):
        p300s.aspirate(160, kappa_mm)
        for w in range(8):
            p300s.dispense(17.5, thermocycler_plate.wells()[w+c])
            p300s.touch_tip()
        p300s.blow_out(kappa_mm)
    p300s.drop_tip()


    #Transfer from DNA plate
    DNACols = DNA_plate.columns()[0:nCols]
    thermoCols = thermocycler_plate.columns()[0:nCols]
    primerCols = primer_plate.columns()[0:nCols]


    p20m.transfer(2.5, primerCols, thermoCols, new_tip="always", touch_tip=True, mix_after=(1, 10))
    p20m.transfer(2.5, DNACols, thermoCols, new_tip="always", mix_after=(2, 20), touch_tip=True)

    ctx.pause("Add plate seal to PCR Plate")
    #Function to define PCR cycle
    def stp(temp, hold):
        return {"temperature": temp, "hold_time_seconds": hold}
    steps = []
    steps.append(stp(95, 30))
    steps += [item for sublist in [[stp(95, 10), stp(55, 30), stp(72, 30)]
                                   for _ in range(0, 12)] for item in sublist]
    steps.append(stp(72, 300))
    steps.append(stp(4, 10))

    thermocycler.close_lid()
    thermocycler.set_lid_temperature(99)
    thermocycler.execute_profile(
        steps=steps,
        repetitions=1, block_max_volume=25)

    thermocycler.open_lid()
