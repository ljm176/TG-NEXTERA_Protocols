def get_values(*names):
    import json
    _all_values = json.loads("""{"pipette_type":"p300_multi_gen2","pipette_mount":"right",
                             "sample_number":16,
                             "zone_384":1,
                             "PCR_volume":60,
                             "bead_ratio":0.8,
                             "elution_buffer_volume":30,
                             "incubation_time":5,
                             "settling_time":1,
                             "drying_time":15
                             }""")
    return [_all_values[n] for n in names]


import math

metadata = {
    'protocolName': '96 WP DNA Purification with Omega biotek beads',
    'author': 'Jeremy Armetta',
    'source': '',
    'apiLevel': '2.9'
}


def run(protocol_context):
    [pipette_type, pipette_mount, sample_number, zone_384, PCR_volume, bead_ratio,
     elution_buffer_volume, incubation_time, settling_time,
     drying_time] = get_values(  # noqa: F821
        "pipette_type", "pipette_mount", "sample_number", "zone_384", "PCR_volume",
        "bead_ratio", "elution_buffer_volume", "incubation_time",
        "settling_time", "drying_time")

    mag_deck = protocol_context.load_module('magdeck', '7')
    mag_plate = mag_deck.load_labware(
        'biorad_96_wellplate_200ul_pcr')
    output_plate = protocol_context.load_labware(
        'greiner_384_wellplate_130ul', '2', 'output plate')
    # opentrons_96_filtertiprack_200ul
    # opentrons_96_tiprack_300ul
    binding_tips = protocol_context.load_labware(
        'opentrons_96_filtertiprack_200ul', '5')
    ethanol_tips = protocol_context.load_labware(
        'opentrons_96_filtertiprack_200ul', '3')

    pip_range = pipette_type.split('_')[0]
    if pip_range == 'p1000':
        tip_name = 'opentrons_96_tiprack_1000ul'
    elif pip_range == 'p300' or range == 'p50':
        tip_name = 'opentrons_96_tiprack_300ul'
    elif pip_range == 'p20':
        tip_name = 'opentrons_96_tiprack_20ul'
    else:
        tip_name = 'opentrons_96_tiprack_10ul'

    tipracks = [binding_tips, ethanol_tips]
    
    pipette = protocol_context.load_instrument(
        pipette_type, pipette_mount, tip_racks=tipracks)
    
    mode = pipette_type.split('_')[1]
    if mode == 'single':
        if sample_number <= 5:
            reagent_container = protocol_context.load_labware(
                'opentrons_24_tuberack_generic_2ml_screwcap',
                '1',
                'reagent rack'
            )
            liquid_waste = protocol_context.load_labware(
                'moas_12rows',
                '1',
                'reservoir for waste').wells()[-1]

        else:
            reagent_container = protocol_context.load_labware(
                'moas_12rows', '1', 'reagent reservoir')
            liquid_waste = reagent_container.wells()[-1]
            liquid_waste_2 = reagent_container.wells()[-2]
            liquid_waste_3 = reagent_container.wells()[-3]
        samples = [well for well in mag_plate.wells()[:sample_number]]
        samples_top = [well.top() for well in samples]
        
            
    else:
        reagent_container = protocol_context.load_labware(
            'moas_12rows', '1', 'reagent reservoir')
        liquid_waste = reagent_container.wells()[-1]
        liquid_waste_2 = reagent_container.wells()[-2]
        liquid_waste_3 = reagent_container.wells()[-3]
        col_num = math.ceil(sample_number/8)
        samples = [col for col in mag_plate.rows()[0][:col_num]]
        samples_top = [well.top() for well in mag_plate.rows()[0][:col_num]]
        
    
    wells = int(sample_number)
    to_process = []   
    for i in range(0, wells, 8):
        to_process.append(i)

    if zone_384 == 1:
        output = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177]
    elif zone_384 == 2:
        output = [192, 208, 224, 240, 256, 272, 288, 304, 320, 336, 352, 368]
    else :
        output = [193, 209, 225, 241, 257, 273, 289, 305, 321, 337, 353, 369]
        
    # Define reagents and liquid waste
    # binding_buffer= reagent_container.wells()[0]
    beads = reagent_container.wells()[0]. bottom(z=1.5)
    ethanol_1 = reagent_container.wells()[1]
    ethanol_2 = reagent_container.wells()[2]
    elution_buffer = reagent_container.wells()[3]

    # Define bead and mix volume to resuspend beads
    bead_volume = PCR_volume*bead_ratio
    if mode == 'single':
        if bead_volume*sample_number > pipette.max_volume:
            mix_vol = pipette.max_volume
        else:
            mix_vol = bead_volume*sample_number
    else:
        if bead_volume*col_num > pipette.max_volume:
            mix_vol = pipette.max_volume
        else:
            mix_vol = bead_volume*col_num
    # binding_vol = PCR_volume*2
    total_vol = bead_volume + PCR_volume # + binding_vol
    
    pipette.flow_rate.aspirate = 150
    pipette.flow_rate.dispense = 150

    # Disengage MagDeck
    mag_deck.disengage()

    # Add binding buffer to samples
    # for target in samples_top:
    #    pipette.pick_up_tip()
    #    pipette.transfer(binding_vol, binding_buffer, target,new_tip='never', touch_tip = True, mix_before=(2, 150), blow_out=True, trash=False)
    #    return tip and reset count
    #    pipette.return_tip()
    # pipette.reset_tipracks()
        
    # Mix beads and PCR 
    # #change for aspirate/mix/touch tip in reservoir and plate since beads ar sticky
    for target, process in zip(samples, to_process):
        pipette.pick_up_tip(binding_tips.wells()[process])
        pipette.mix(3, 180, beads)
        pipette.aspirate(bead_volume, beads)
        pipette.move_to(reagent_container.wells()[0].top(z=1))
        protocol_context.delay(seconds = 3.0)
        pipette.touch_tip(reagent_container.wells()[0])
        pipette.dispense(bead_volume, target)
        pipette.mix(6, total_vol, target)
        pipette.touch_tip(target)
        # return tip and reset count
        pipette.return_tip()
    pipette.reset_tipracks()

    # Incubate beads and PCR product at RT
    protocol_context.comment("Incubating the beads and PCR products at room temperature for " 
                             + str(incubation_time) + " minutes. Protocol will resume automatically.")
    protocol_context.delay(minutes=incubation_time)

    # Engage MagDeck and Magnetize
    mag_deck.engage()
    protocol_context.comment("Delaying for "+str(settling_time)+" minutes for beads to settle.")
    protocol_context.delay(minutes=settling_time)

    # Remove supernatant from magnetic beads
    pipette.flow_rate.aspirate = 50
    for target,process in zip(samples, to_process):
        pipette.pick_up_tip(binding_tips.wells()[process])
        pipette.transfer(total_vol, target.bottom(0.7), liquid_waste.top(), touch_tip=True, new_tip='never', 
                         blow_out=False, blowout_location='destination well') #check the height and volume with .bottom
        pipette.drop_tip(binding_tips.wells()[process])
    pipette.flow_rate.aspirate = 100
    
    # Wash beads 2 times with 70% ethanol
    air_vol = pipette.max_volume*0.1

    #for target,process in zip(samples, to_process):
    #    pipette.pick_up_tip(ethanol_tips.wells()[process])
    #    pipette.transfer(150, ethanol_1, target.bottom(z=1.5),new_tip='never', 
    # air_gap=air_vol, blow_out=True, blowout_location='destination well', trash=False)
    #    pipette.drop_tip(binding_tips.wells()[process])
    #pipette.reset_tipracks()

    pipette.pick_up_tip(ethanol_tips.wells()[0])
    for target in samples:
        pipette.transfer(150, ethanol_1.bottom(3), target.top(z=1),new_tip='never', 
                         air_gap=air_vol, blow_out=True, blowout_location='destination well', trash=False, touch_tip=True )
    pipette.drop_tip(ethanol_tips.wells()[0])
    pipette.reset_tipracks()

    msg = "Delaying for 30 seconds."
    protocol_context.delay(seconds=30, msg=msg)
    
    pipette.flow_rate.aspirate = 50
    
    for target, process in zip(samples, to_process):
        pipette.pick_up_tip(binding_tips.wells()[process])
        pipette.transfer(160, target.bottom(z=1.5), liquid_waste.top(),new_tip='never',touch_tip=True, air_gap=air_vol) 
        pipette.drop_tip(binding_tips.wells()[process])
    
    pipette.flow_rate.aspirate = 150
    
    pipette.pick_up_tip(ethanol_tips.wells()[0])
    for target in samples:
        pipette.transfer(150, ethanol_2.bottom(3), target.top(z=1),new_tip='never', 
                         air_gap=air_vol, blow_out=True, blowout_location='destination well', trash=False)
    pipette.drop_tip(ethanol_tips.wells()[0])
    pipette.reset_tipracks()

    msg = "Delaying for 30 seconds."
    protocol_context.delay(seconds=30, msg=msg)
    
    pipette.flow_rate.aspirate = 50
    
    for target, process in zip(samples, to_process):
        pipette.pick_up_tip(binding_tips.wells()[process])
        pipette.aspirate(90, target.bottom(z=1))
        pipette.aspirate(60, target.bottom(z=0.6))
        protocol_context.delay(seconds=5.0)
        pipette.aspirate(20, target.bottom(z=0.1))
        pipette.aspirate(20, target.bottom(z=0.02))
        pipette.touch_tip()
        pipette.dispense(200, liquid_waste_2.top())
        pipette.touch_tip()
        pipette.drop_tip()
    
    pipette.flow_rate.aspirate = 150 
    
    # Dry at RT
    msg = "Drying the beads for " + str(drying_time) + " minutes. Protocol will resume automatically."
    protocol_context.delay(minutes=drying_time, msg=msg)

    # Disengage MagDeck
    mag_deck.disengage()

    # wash ethanol tips
    pipette.pick_up_tip(ethanol_tips.wells()[0])
    for x in range(3):
        pipette.transfer(150, elution_buffer.bottom(z=3), liquid_waste_2.top(), new_tip='never', touch_tip=True)
    pipette.drop_tip(ethanol_tips.wells()[0])

    # Mix beads with elution buffer
    if elution_buffer_volume/2 > pipette.max_volume:
        mix_vol = pipette.max_volume
    else:
        mix_vol = elution_buffer_volume/2
    pipette.flow_rate.aspirate = 50
    pipette.flow_rate.dispense = 100

    for target, process in zip(samples, to_process):
        pipette.pick_up_tip(ethanol_tips.wells()[process])
        pipette.transfer(elution_buffer_volume, elution_buffer, target.bottom(z = 2.5), mix_after=(20, 10), new_tip='never', blow_out=False)
        protocol_context.delay(seconds=8.0)
        pipette.mix(10, mix_vol, target.bottom(z=1))
        pipette.touch_tip()
        pipette.drop_tip(ethanol_tips.wells()[process])
    pipette.reset_tipracks()
    
    # Incubate at RT for 3 minutes
    protocol_context.comment("Incubating at room temperature for 3 minutes. Protocol will resume automatically.")
    protocol_context.delay(minutes=3)

    # Engage MagDeck for 1 minute and remain engaged for DNA elution
    mag_deck.engage()
    protocol_context.comment("Delaying for "+str(settling_time)+" minutes for beads to settle.")
    protocol_context.delay(minutes=settling_time)
    pipette.flow_rate.aspirate = 20

    # Transfer clean PCR product to a new well
    for target, dest, process in zip(samples, output, to_process):
        pipette.pick_up_tip(ethanol_tips.wells()[process])
        pipette.transfer(elution_buffer_volume, target.bottom(z=1), output_plate.wells()[dest].top(z=1), new_tip='never', 
                         touch_tip=True, blow_out=True, blowout_location='destination well') # check the height with .bottom
        pipette.drop_tip()
    # Disengage MagDeck
    mag_deck.disengage()
