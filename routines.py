#!/usr/bin/env python3
"""
@author: Luis I. Reyes Castro
"""

import pandas as pd
from models import Motor, Propeller, ElectronicSpeedController
from models import PropulsionSysConf, PowerSysConf
from models import Battery

def parse_Propulsion_Systems( motor_pathname,
                              propeller_pathname,
                              include_low_voltage = False) :
    """
    Parses propulsion system configurations from XLSX files.
    """

    handle = open( motor_pathname, 'rb')
    motor_df = pd.read_excel( handle, sheet_name = 'Motor-specs')
    handle.close()

    motor = Motor(motor_df)
    if ( not include_low_voltage ) and motor.cells < 8 :
        return []

    print( 'Loading motor data from: ' + motor_pathname )
    handle = open( motor_pathname, 'rb')
    props_df = pd.read_excel( handle, sheet_name = 'Prop-specs')
    handle.close()

    print( 'Loading propeller data from: ' + propeller_pathname )
    handle = open( propeller_pathname, 'rb')
    pd_df = pd.read_excel( handle, sheet_name = motor.brand)
    handle.close()

    propellers = []
    for ( index, row) in props_df.iterrows() :

        sheet_to_read = str( row['Sheet'] )

        diameter     = row['Diameter']
        thread       = row['Thread']
        blades       = row['Blades']
        test_voltage = row['Test Voltage (V)']

        print( '\t' + 'Loading performance data for propeller: ' +
               str(diameter) + ' x ' + str(thread) + ' x ' + str(blades) )

        handle       = open( motor_pathname, 'rb')
        test_data_df = pd.read_excel( handle, sheet_to_read)
        handle.close()

        row__ = pd_df[ ( pd_df['Diameter (in)'] == diameter ) & \
                       ( pd_df['Blades'] == blades ) ].iloc[0]

        prop_weight = row__['Weight per Blade (g)'] * blades / 1000.0
        prop_cost   = row__['Price per Pair (USD)'] / 2.0

        propeller = Propeller( motor.brand,
                               diameter, thread, blades,
                               test_voltage, test_data_df,
                               prop_weight, prop_cost )

        propellers.append( propeller)

    configurations = []
    for propeller in propellers :
        quadrotor = PropulsionSysConf( motor, propeller, 4)
        octorotor = PropulsionSysConf( motor, propeller, 8)
        configurations.append( quadrotor)
        configurations.append( octorotor)

    return configurations

def parse_Power_Systems( pathname, max_Watthours_per_pack = 100) :
    """
    Parses propulsion system configurations from battery data in an
    XLSX file.
    """

    print( 'Loading battery data from:', pathname)
    handle = open( pathname, 'rb')
    df = pd.read_excel( handle, sheet_name = 'All-brands')
    handle.close()

    batteries     = []
    S04_batteries = []
    S06_batteries = []

    for ( index, row) in df.iterrows() :

        battery = Battery( row['Brand'],
                           row['Model'],
                           row['Cells'],
                           row['Capacity (mAh)'],
                           row['MCR'],
                           row['MCDR'],
                           row['Weight (g)'] / 1000.0,
                           row['Price (USD)'] )

        if battery.energy_Watthours < max_Watthours_per_pack :
            batteries.append(battery)
            if battery.cells == 4 :
                S04_batteries.append(battery)
            if battery.cells == 6 :
                S06_batteries.append(battery)

    for S04_bat in S04_batteries :
        for S06_bat in S06_batteries :
            if S04_bat.brand == S06_bat.brand and \
               S04_bat.model == S06_bat.model and \
               S04_bat.capacity == S06_bat.capacity :
                brand    = S04_bat.brand
                model    = S06_bat.model
                cells    = 10
                capacity = S04_bat.capacity
                mcr      = min( [ S04_bat.mcr,  S06_bat.mcr ] )
                mcdr     = min( [ S04_bat.mcdr, S06_bat.mcdr] )
                weight   = S04_bat.weight + S06_bat.weight
                cost     = S04_bat.cost   + S06_bat.cost
                battery  = Battery( brand, model, cells, capacity,
                                    mcr, mcdr, weight, cost)
                batteries.append(battery)

    power_sys_confs = []

    for battery in batteries :

        if battery.cells == 4 :
            S08_P2 = PowerSysConf( battery, 2, 2)
            S08_P4 = PowerSysConf( battery, 2, 4)
            power_sys_confs.append( S08_P2)
            power_sys_confs.append( S08_P4)

        if battery.cells == 5 :
            S10_P2 = PowerSysConf( battery, 2, 2)
            S10_P4 = PowerSysConf( battery, 2, 4)
            power_sys_confs.append( S10_P2)
            power_sys_confs.append( S10_P4)

        if battery.cells == 6 :

            S06_P2 = PowerSysConf( battery, 1, 2)
            S06_P4 = PowerSysConf( battery, 1, 4)
            power_sys_confs.append( S06_P2)
            power_sys_confs.append( S06_P4)

            S12_P2 = PowerSysConf( battery, 2, 2)
            S12_P4 = PowerSysConf( battery, 2, 4)
            power_sys_confs.append( S12_P2)
            power_sys_confs.append( S12_P4)

        if battery.cells == 8 :
            S08_P2 = PowerSysConf( battery, 1, 2)
            S08_P4 = PowerSysConf( battery, 1, 4)
            power_sys_confs.append( S08_P2)
            power_sys_confs.append( S08_P4)

        if battery.cells == 10 :
            S10_P2 = PowerSysConf( battery, 1, 2)
            S10_P4 = PowerSysConf( battery, 1, 4)
            power_sys_confs.append( S10_P2)
            power_sys_confs.append( S10_P4)

    return power_sys_confs

def parse_ESC_Data( pathname, brand_name) :
    """
    Parses electronic speed controller (ESC) data from an XLSX file.
    """

    print( 'Loading electronic speed controller (ESC) data from:', pathname)
    handle = open( pathname, 'rb')
    df = pd.read_excel( handle, sheet_name = brand_name)
    handle.close()

    sorted_esc_list = []
    for ( index, row) in df.iterrows() :
        esc = ElectronicSpeedController( brand_name,
                                         row['Model'],
                                         row['Max Cells (S)'],
                                         row['Rating (A)'],
                                         row['Weight (g)'] / 1000.0,
                                         row['Price (USD)'] )
        sorted_esc_list.append(esc)

    return sorted_esc_list

def pareto_frontier( vehicle_confs) :
    """
    Computes the pareto frontier of vehicle configurations.
    Reference: http://code.activestate.com/recipes/578230-pareto-front/
    """

    vehicle_confs.sort( key = lambda vehicle : vehicle.massbudget,
                        reverse = True)

    frontier = [ vehicle_confs[0] ]
    interior = []
    for vehicle in vehicle_confs[1:] :
        if vehicle.endurance > frontier[-1].endurance :
            frontier.append(vehicle)
        else :
            interior.append(vehicle)

    return frontier, interior
