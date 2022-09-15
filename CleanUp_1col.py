metadata = {
    'apiLevel': '2.8',
    'protocolName': 'TG Nextera XT - Clean Up',
    'author': 'Lachlan Munro (lajamu@biosustain.dtu.dk',
}


#Parts of protocol modified from Opentrons protocol library

#Set number of samples (Note that protocol will run full columns)


def run(ctx):

    nCols = 1

    mag_deck = ctx.load_module('magnetic module gen2', '4')
    mag_deck.disengage()
    mag_plate = mag_deck.load_labware(
        'armadillo_pcr_200')

    reservoir_12 = ctx.load_labware('moas_12rows', 2)
    beads = reservoir_12.wells_by_name()["A1"]
    h2o = reservoir_12.wells_by_name()["A2"]

    etoh_res = ctx.load_labware("agilent_1_reservoir_290ml", 5)
    etoh = etoh_res["A1"]
    liq_trash_res = ctx.load_labware("usascientific_96_wellplate_2.4ml_deep", 7)

    clean_DNA = ctx.load_labware("armadillo_pcr_200", 1)


    t1 = ctx.load_labware("opentrons_96_tiprack_300ul", 3)
    t2 = ctx.load_labware("opentrons_96_tiprack_300ul", 6)
    t3 = ctx.load_labware("opentrons_96_tiprack_300ul", 8)
    t4 = ctx.load_labware("opentrons_96_tiprack_300ul", 9)
    t5 = ctx.load_labware("opentrons_96_tiprack_300ul", 11)
    
    
    p300m = ctx.load_instrument(
        "p300_multi_gen2",
        "right",
        tip_racks=[t1, t2, t3, t4, t5])

    #Tip use tracker
    tips = [t.columns()[c][0] for t in p300m.tip_racks for c in range(12)]
    st = 0



    mag_cols = mag_plate.columns()[0:nCols]
    liq_trash_cols = liq_trash_res.columns()[0:nCols]
    dna_cols = clean_DNA.columns()[0:nCols]


    p300m.transfer(41, beads, mag_cols, mix_before = (2, 200), mix_after=(3, 50), new_tip="always")
    st += nCols

    #Five minute incubation
    ctx.delay(300)
    #10 minute incubation on mag deck
    mag_deck.engage(height=10)
    ctx.delay(300)

    p300m.transfer(300, mag_cols, liq_trash_cols, new_tip="always")
    st += nCols


    def add_Remove_Etoh(start_tip, trash_tips=False):
        """
        Washes with ethanol, designed to reuse tips to save plastic.
        """
        p300m.pick_up_tip(tips[start_tip + nCols])
        p300m.transfer(100, etoh, [col[0].top() for col in mag_cols], new_tip="never")
        if trash_tips:
        	p300m.drop_tip()
        else:
        	p300m.return_tip()


        #Can add ethanol incubation here if neccesary
        p300m.reset_tipracks()
        p300m.starting_tip = tips[start_tip]
        for col in list(range(nCols)):
            p300m.pick_up_tip()
            p300m.aspirate(100, mag_cols[col][0])
            p300m.aspirate(100, mag_cols[col][0].bottom(0.5))
            p300m.aspirate(100, mag_cols[col][0].bottom(0.2))
            p300m.dispense(300, liq_trash_cols[col][0])
            p300m.touch_tip()
            p300m.aspirate(100, mag_cols[col][0])
            p300m.aspirate(100, mag_cols[col][0].bottom(0.5))
            p300m.aspirate(100, mag_cols[col][0].bottom(0.1))
            p300m.dispense(300, liq_trash_cols[col][0])
            p300m.touch_tip()

            if trash_tips:
                p300m.drop_tip()
            else:
                p300m.drop_tip(tips[start_tip])



    def wash():
    	add_Remove_Etoh(st)
    	add_Remove_Etoh(st, trash_tips=True)	

    wash()
    st += (nCols + 1)
    p300m.reset_tipracks()
    p300m.starting_tip = tips[st]
    #ctx.pause("Remove excess ethanol and return plate to mag-deck then click resume")

    ctx.delay(600)    
    mag_deck.disengage()
    p300m.transfer(45, h2o, [col[0].top() for col in mag_cols], new_tip="once")
    st += 1
    ctx.delay(180)
    mag_deck.engage(height=10)
    ctx.delay(600)

    p300m.transfer(35, mag_cols, dna_cols, new_tip="always", touch_tip=True)








