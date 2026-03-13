import json
import sys

# Parameters derived from historical data analysis.
# Model:
# lap_time = base_lap_time + compound_offset + degradation(age, tire, temp)
# degradation starts after an initial cliff period for each compound.
SOFT_OFFSET = -0.844739
HARD_OFFSET = 0.182246
SOFT_DEG_RATE = 0.167991
MED_DEG_RATE = 0.059281
HARD_DEG_RATE = 0.036989
SOFT_CLIFF = 3.0
MED_CLIFF = 5.0
HARD_CLIFF = 8.0
TEMP_COEFF = 0.004072
REF_TEMP = 15.979670

COMPOUND_OFFSET = {
    'SOFT': SOFT_OFFSET,
    'MEDIUM': 0.0,
    'HARD': HARD_OFFSET,
}

DEGRADATION_RATE = {
    'SOFT': SOFT_DEG_RATE,
    'MEDIUM': MED_DEG_RATE,
    'HARD': HARD_DEG_RATE,
}

CLIFF_LAPS = {
    'SOFT': SOFT_CLIFF,
    'MEDIUM': MED_CLIFF,
    'HARD': HARD_CLIFF,
}


def simulate_driver(strategy, race_config):
    total_laps = race_config['total_laps']
    base_lap_time = race_config['base_lap_time']
    pit_lane_time = race_config['pit_lane_time']
    track_temp = race_config['track_temp']

    temp_modifier = 1.0 + TEMP_COEFF * (track_temp - REF_TEMP)
    pit_schedule = {pit['lap']: pit['to_tire'] for pit in strategy.get('pit_stops', [])}

    total_time = 0.0
    current_tire = strategy['starting_tire']
    tire_age = 0

    for lap in range(1, total_laps + 1):
        tire_age += 1
        effective_age = max(0.0, tire_age - CLIFF_LAPS[current_tire])
        degradation = DEGRADATION_RATE[current_tire] * effective_age * temp_modifier
        lap_time = base_lap_time + COMPOUND_OFFSET[current_tire] + degradation
        total_time += lap_time

        if lap in pit_schedule:
            total_time += pit_lane_time
            current_tire = pit_schedule[lap]
            tire_age = 0

    return total_time


def predict_finishing_positions(test_case):
    race_config = test_case['race_config']
    strategies = test_case['strategies']

    driver_times = []
    for _, strategy in strategies.items():
        driver_id = strategy['driver_id']
        total_time = simulate_driver(strategy, race_config)
        driver_times.append((total_time, driver_id))

    driver_times.sort()
    return [driver_id for _, driver_id in driver_times]


def main():
    test_case = json.load(sys.stdin)
    result = {
        'race_id': test_case['race_id'],
        'finishing_positions': predict_finishing_positions(test_case),
    }
    json.dump(result, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
