#!/usr/bin/env python3
"""
@author: Luis I. Reyes Castro
"""

import pandas as pd

class Motor :
    """
    Implementation of a Motor.
    """
    def __init__( self, motor_specs_df) :
        df          = pd.DataFrame(motor_specs_df)
        self.brand  = df[ df['Attribute'] == 'Brand' ]['Value'].iloc[0]
        self.model  = df[ df['Attribute'] == 'Model' ]['Value'].iloc[0]
        self.kv     = df[ df['Attribute'] == 'KV' ]['Value'].iloc[0]
        self.cells  = df[ df['Attribute'] == 'Cells' ]['Value'].iloc[0]
        self.max_I  = df[ df['Attribute'] == 'Max Current' ]['Value'].iloc[0]
        self.max_P  = df[ df['Attribute'] == 'Max Power' ]['Value'].iloc[0]
        self.weight = df[ df['Attribute'] == 'Weight' ]['Value'].iloc[0] / 1000.0
        self.cost   = df[ df['Attribute'] == 'Unit Price' ]['Value'].iloc[0]
        self.id = self. brand + '_' + self.model + '_' + str(self.cells) + 'S'
        return

class Propeller :
    """
    Implementation of a Propeller.
    """
    def __init__( self, brand,
                        diameter,
                        thread,
                        blades,
                        test_voltage,
                        test_data_df,
                        weight,
                        cost) :
        self.brand    = brand
        self.diameter = diameter
        self.thread   = thread
        self.blades   = blades
        self.voltage  = test_voltage
        self.data     = pd.DataFrame(test_data_df)
        self.weight   = weight
        self.cost     = cost
        self.data['Thrust (g)'] /= 1000.0
        self.id = self.brand + '_' \
                + str(self.diameter) + '-' \
                + str(self.thread) + '-' \
                + str(self.blades)
        return

class PropulsionSysConf :
    """
    Implementation of a Propulsion System Configuration, which is specified
    by a motor, a propeller, and the number of motors onboard the vehicle.
    """
    def __init__( self, motor, propeller, num_motors) :
        self.id         = [ motor.id, propeller.id]
        self.motor      = motor
        self.propeller  = propeller
        self.num_motors = num_motors
        self.cells      = motor.cells
        self.weight = motor.weight     * num_motors \
                    + propeller.weight * num_motors
        self.cost   = motor.cost     * num_motors \
                    + propeller.cost * num_motors
        return

    def getHoverData( self, according_to, thrust_to_weight_ratio = 2.0) :
        df = self.propeller.data.set_index('Throttle (%)')
        if according_to == 'throttle' :
            unit_thrust  = df.loc[50]['Thrust (g)']
            unit_current = df.loc[50]['Current (A)']
            unit_power   = df.loc[50]['Power (W)']
        elif according_to == 'thrust' :
            max_thrust  = df.loc[100]['Thrust (g)']
            unit_thrust = max_thrust / thrust_to_weight_ratio
            df.reset_index( inplace = True)
            df.loc[-1] = [ None, None, None, None, unit_thrust]
            df.set_index( 'Thrust (g)', inplace = True)
            df.sort_index( inplace = True)
            df.interpolate( method = 'index', inplace = True)
            unit_current = df.loc[unit_thrust]['Current (A)']
            unit_power   = df.loc[unit_thrust]['Power (W)']
        else :
            raise ValueError
        hover_data = { 'unit_thrust' : unit_thrust,
                       'unit_current': unit_current,
                       'unit_power'  : unit_power,
                       'thrust'  : unit_thrust  * self.num_motors,
                       'current' : unit_current * self.num_motors,
                       'power'   : unit_power   * self.num_motors }
        return hover_data

    def getMaxThrottleData( self) :
        df = self.propeller.data.set_index('Throttle (%)')
        unit_thrust  = df.loc[100]['Thrust (g)']
        unit_current = df.loc[100]['Current (A)']
        unit_power   = df.loc[100]['Power (W)']
        maxthrottle_data = { 'unit_thrust' : unit_thrust,
                             'unit_current': unit_current,
                             'unit_power'  : unit_power,
                             'thrust'  : unit_thrust  * self.num_motors,
                             'current' : unit_current * self.num_motors,
                             'power'   : unit_power   * self.num_motors }
        return maxthrottle_data

class Battery :
    """
    Implementation of a Battery.
    """
    def __init__( self, brand,
                        model,
                        cells,
                        capactity,
                        max_charge_rate_in_Cs,
                        max_cont_discharge_rate_in_Cs,
                        weight,
                        cost,
                        is_stack = False) :
        self.brand = brand
        self.model = model
        self.cells    = cells
        self.capacity = capactity
        self.C        = capactity / 1000.0
        self.mcr      = max_charge_rate_in_Cs
        self.mcdr     = max_cont_discharge_rate_in_Cs
        self.weight   = weight
        self.cost     = cost
        self.is_stack = is_stack
        self.voltage          = 3.7 * self.cells
        self.capacity_Coulomb = 3.6 * self.capacity
        self.energy_Watthours = self.voltage * self.C
        self.energy_Joules    = self.voltage * self.capacity_Coulomb
        self.max_current      = self.C * self.mcdr
        self.id = self.brand + '_' + self.model + '_' \
                + str(self.cells) + 'S_' \
                + str(self.capacity) + 'mAh_' \
                + str(self.mcdr) + 'C'
        if self.is_stack :
            self.id += '_Stack'
        return

class PowerSysConf :
    """
    Implementation of a Power System Configuration, which includes one or
    more batteries in series or parallel connection.
    """
    def __init__( self, battery, num_series = 1, num_parallel = 1) :
        self.battery   = battery
        self.num_ser   = num_series
        self.num_par   = num_parallel
        self.num_packs = num_series * num_parallel
        self.cells    = battery.cells    * num_series
        self.capacity = battery.capacity * num_parallel
        self.C        = battery.C        * num_parallel
        self.mcr      = battery.mcr      * num_parallel
        self.mcdr     = battery.mcdr     * num_parallel
        self.weight   = battery.weight   * self.num_packs
        self.cost     = battery.cost     * self.num_packs
        self.voltage          = 3.7 * self.cells
        self.capacity_Coulomb = 3.6 * self.capacity
        self.energy_Watthours = self.voltage * self.C
        self.energy_Joules    = self.voltage * self.capacity_Coulomb
        self.max_current      = self.C * self.mcdr
        return

class ElectronicSpeedController :
    """
    Implementation of an Electronic Speed Controller (ESC).
    """
    def __init__( self, brand, model, max_cells, rating, weight, cost) :
        self.brand       = brand
        self.model       = model
        self.max_cells   = max_cells
        self.max_current = rating
        self.weight      = weight
        self.cost        = cost
        self.max_voltage = 3.7 * self.max_cells
        return

class VehicleConfiguration :
    """
    Implementation of a Vehicle configuration, which includes a propulsion
    system configuration, a power system configuration, and an electronic
    speed controller (ESC).
    """
    def __init__( self, propsysconf,
                        powersysconf,
                        esc,
                        size_according_to = 'thrust',
                        thrust_to_weight_ratio = 2.0) :
        self.is_feasible = False
        self.cells      = propsysconf.motor.cells
        self.num_motors = propsysconf.num_motors
        self.esc_weight = esc.weight * self.num_motors
        self.esc_cost   = esc.cost   * self.num_motors
        if self.cells != powersysconf.cells or self.cells > esc.max_cells :
            return
        self.maxthrottle_data = propsysconf.getMaxThrottleData()
        if self.maxthrottle_data['thrust'] < 4.0 * powersysconf.weight :
            return
        if 0.85 * self.maxthrottle_data['current'] > powersysconf.max_current :
            return
        if 0.85 * self.maxthrottle_data['unit_current'] > esc.max_current :
            return
        self.hover_data = propsysconf.getHoverData( size_according_to,
                                                    thrust_to_weight_ratio)
        self.massbudget = self.hover_data['thrust'] \
                        - propsysconf.weight \
                        - powersysconf.weight \
                        - self.esc_weight
        self.endurance  = powersysconf.energy_Joules \
                        / self.hover_data['power'] \
                        / 60.0
        self.cost       = propsysconf.cost \
                        + powersysconf.cost \
                        + self.esc_cost
        if not ( self.massbudget > 0.0 and self.endurance > 0.0 ) :
            return
        self.propsysconf  = propsysconf
        self.powersysconf = powersysconf
        self.esc          = esc
        self.is_feasible = True
        return
