
#================================================
# FLASK POSITIONS BACTALERT
#================================================
WASTE_FLASK = 220  
DECONTAMINATION_CONTROL = 178
HV_FLASK = 136
FLUSH_OUT_FLASK_1 = 96
FLUSH_OUT_FLASK_2 = 55
ZERO_V_FLASK = 14

#================================================
# FLASK POSITIONS FALCONS
#================================================
FALCON_FLASK_1 = 220  
FALCON_FLASK_2 = 170
FALCON_FLASK_3 = 120
FALCON_FLASK_4 = 70
FALCON_FLASK_5 = 20

#================================================
# PIERCING MOTOR MOVEMENT POSITIONS
#================================================
DEPIERCE = 50 
PIERCE = 4

#================================================
# PIERCING MOTOR MOVEMENT TIMES
#================================================
DRIP_T = 30 * 1000
SOAK_T = 60 * 1000 * 5
PIERCE_T = 10000

#================================================
# DEFAULT FLOW RATE VALUES
#================================================
FR = [2.25, 2.5, 5]

#================================================
# DEFAULT VOLUME VALUES
#================================================
V = [5, 10, 11.25] #V[2] = 9mls + 30s of sucrose before and after blood starts. therefore 9 + 2.25/60s *30s *2 = 11.25
