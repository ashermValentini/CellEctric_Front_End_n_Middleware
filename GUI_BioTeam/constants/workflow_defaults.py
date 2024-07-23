
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
# DEFAULT SUCROSE FLOW RATE VALUES WORKFLOWS 
#================================================
FR = [2.25, 2.5, 5]
#================================================
# DEFAULT SUCROSE VOLUME VALUES WORKFLOWS 
#================================================
V = [5, 10, 11.25, 4.05] 
#V[2] = 9mls + 30s of sucrose before and after blood starts. therefore 9 + 2.25/60s *30s *2 = 11.25 (Human Blood WF) 
#V[3] = 1.8ml + 30s of sucrose before and after bloos starts/stops. Therefore 1.8 + 2.25/60s *30s *2 = 4.05 (Mouse Blood WF)
#================================================
# DEFAULT BLOOD FLOW RATE VALUES WORKFLOWS 
#================================================
BLOOD_FR = [0.25]
#================================================
# DEFAULT BLOOD VOLUME VALUES WORKFLOWS 
#================================================
BLOOD_V = [1, 0.2] 
#BLOOD_V[0] for Human Blood/POCII workflow 
#BLOOD_V[1] for Mouse Blood workflow
#================================================
# DIRECTIONS FOR MOTORS 
#================================================

DIR_M1_UP = 1
DIR_M1_DOWN = -1
DIR_M2_UP = -1
DIR_M2_DOWN = 1
DIR_M3_RIGHT = 1
DIR_M3_LEFT = 2
DIR_M4_UP = 2
DIR_M4_DOWN = 1


