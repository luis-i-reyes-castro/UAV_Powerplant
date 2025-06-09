#!/usr/bin/env python3
"""
@author: Luis I. Reyes-Castro
"""

import os
import matplotlib.pyplot as plt
from models import VehicleConfiguration
from routines import parse_Propulsion_Systems
from routines import parse_Power_Systems
from routines import parse_ESC_Data
from routines import pareto_frontier

motor_brand      = 'KDE'
motor_data_dir   = 'Propulsion-Systems/' + motor_brand + '/'
motor_data_files = os.listdir( motor_data_dir)
motor_data_files.sort()

propeller_data_path = 'Propellers.xlsx'

prop_sys_confs = []
for motor_data_file in motor_data_files :
    motor_data_path = motor_data_dir + motor_data_file
    prop_sys_confs += parse_Propulsion_Systems( motor_data_path,
                                                propeller_data_path)

battery_files   = 'Batteries.xlsx'
power_sys_confs = parse_Power_Systems( battery_files, 1000)

esc_files       = 'Electronic-Speed-Controllers.xlsx'
sorted_esc_list = parse_ESC_Data( esc_files, brand_name = 'KDE')

vehicle_confs  = []
min_endurance  = 15.0
min_massbudget = 10.0
max_cost       = 5500

print( 'Computing set of all feasible vehicle configurations...' )
for propsysconf in prop_sys_confs :
    for powersysconf in power_sys_confs :
        for esc in sorted_esc_list :
            vehicle = VehicleConfiguration( propsysconf, powersysconf, esc)
            if vehicle.is_feasible and \
               vehicle.massbudget >= min_massbudget and \
               vehicle.endurance >= min_endurance and \
               vehicle.cost <= max_cost :
                   vehicle_confs.append(vehicle)
                   break

print( 'Computing pareto frontier of vehicle configurations...' )
frontier, interior = pareto_frontier( vehicle_confs)

frontier_quad = []
frontier_octo = []
for vehicle in frontier :
    if vehicle.propsysconf.num_motors == 4 :
        frontier_quad.append(vehicle)
    elif vehicle.propsysconf.num_motors == 8 :
        frontier_octo.append(vehicle)

xf_4 = [ vehicle.massbudget for vehicle in frontier_quad ]
xf_8 = [ vehicle.massbudget for vehicle in frontier_octo ]
xi   = [ vehicle.massbudget for vehicle in interior ]
yf_4 = [ vehicle.endurance for vehicle in frontier_quad ]
yf_8 = [ vehicle.endurance for vehicle in frontier_octo ]
yi   = [ vehicle.endurance for vehicle in interior ]

plt.figure( figsize = (8,6), dpi = 90)
plt.scatter( xi,   yi,   c = 'green')
plt.scatter( xf_4, yf_4, c = 'blue')
plt.scatter( xf_8, yf_8, c = 'red')

plt.axis('tight')
plt.xlabel( 'Mass Budget [kg]' )
plt.ylabel( 'Hover Flight Endurance [min]' )
plt.legend( [ 'Dominated configurations',
              'Pareto Quadcopters',
              'Pareto Octocopters' ] )
plt.title( 'Brand: ' + motor_brand + ' - Maximum cost: $' + str(max_cost) )
plt.savefig( 'Vehicle-Performance_Brand:' + motor_brand +
             '_Max-cost:' + str(max_cost) + '.pdf' )
plt.show()

print( 'Pareto frontier of vehicle configurations:' )
for ( i, vehicle_conf) in enumerate(frontier) :
    print( '[+] Configuration ' + str(i+1) + ':' )
    print( '\t' + 'Mass budget / Endurance: ' \
                + str(vehicle_conf.massbudget) + ' kg / ' \
                + str(vehicle_conf.endurance) + ' min' )
    print( '\t' + 'Motor: ' + vehicle_conf.propsysconf.id[0] )
    print( '\t' + 'Propeller: ' + vehicle_conf.propsysconf.id[1] )
    print( '\t' + 'Number of motors: ' + str(vehicle_conf.num_motors) )
    print( '\t' + 'Battery pack: ' \
                + vehicle_conf.powersysconf.battery.id )
    print( '\t' + 'Number of battery packs: ' \
                + str(vehicle_conf.powersysconf.num_packs) )
