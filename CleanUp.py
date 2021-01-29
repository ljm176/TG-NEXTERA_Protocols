metadata = {
    'apiLevel': '2.5',
    'protocolName': 'TG Nextera XT index kit - Clean Up',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Custom Protocol Request'
}

from math import ceil

def run(ctx):
    nsamples = 8
    nCols = ceil(nsamples/8)

    mag_deck = ctx.load_module('magnetic module gen2', '4')
    mag_deck.disengage()
    mag_plate = mag_deck.load_labware(
        'nest_96_wellplate_100ul_pcr_full_skirt')

    reservoir_12 = ctx.load_labware('moas_12rows', 2)
    beads = reservoir_12.wells_by_name()["A1"]
    h2o = reservoir_12.wells_by_name()["A2"]

    etoh_res = ctx.load_labware("agilent_1_reservoir_290ml", 5)
    etoh = etoh_res["A1"]
    liq_trash_res = ctx.load_labware("usascientific_96_wellplate_2.4ml_deep", 7)

    clean_DNA = ctx.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", 1)


    t1 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 9)
    t2 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 6)
    t3 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 3)
    t4 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 8)
    t5 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 10)

    if nCols==12: 
        st = t3.wells()[0]
    elif nCols>6:
        st = t2.wells()[8*2*(nCols-6)]
    else:
        st = t1.wells()[8*(2*nCols)]

    p300m = ctx.load_instrument(
        "p300_multi_gen2",
        "left",
        tip_racks=[t1, t2, t3, t4, t5])

    

    mag_cols = mag_plate.columns()[0:nCols]
    liq_trash_cols = liq_trash_res.columns()[0:nCols]
    dna_cols = clean_DNA.columns()[0:nCols]

    p300m.transfer(45, beads, mag_cols, mix_before = (2, 200), mix_after=(3, 50), new_tip="always")
    #Five minute incubation
    ctx.delay(300)

    #10 minute incubation on mag deck
    mag_deck.engage()
    ctx.delay(300)

    p300m.transfer(50, mag_cols, liq_trash_cols, new_tip="always")

    def add_Remove_Etoh(start_tip, trash_tips=False):
        """
        Washes with ethanol, designed to reuse tips to save plastic.
        """
        p300m.pick_up_tip(t4.well("A1"))
        p300m.transfer(100, etoh, [col[0].top() for col in mag_cols], new_tip="never")

        #Can add ethanol incubation here if neccesary
        p300m.return_tip()
        p300m.reset_tipracks()
        p300m.starting_tip = start_tip
        p300m.transfer(200, mag_cols, liq_trash_cols, trash=trash_tips, new_tip="always", touch_tip=True)


    def wash():
    	add_Remove_Etoh(st)
    	add_Remove_Etoh(st, trash_tips=True)

    wash()

    ctx.delay(300)    
    mag_deck.disengage()

    p300m.transfer(45, h2o, mag_cols, mix_after=(10, 50), new_tip="always", trash=False)
    ctx.delay(60)
    mag_deck.engage()
    ctx.delay(180)

    p300m.transfer(35, mag_cols, dna_cols, new_tip="always", touch_tip=True)








