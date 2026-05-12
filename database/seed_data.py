import pandas as pd
import os
import re
import random
from datetime import datetime, timedelta
from database.db import SessionLocal, init_db
from database.models import Patient, PainAssessment, Consultation, Treatment, Conversation, AIOutput, ProgressTracking
from database.crud import calculate_bmi
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data.xlsx")

random.seed(42)

DISEASE_TEMPLATES = {
    "back_pain": {
        "pain_areas": "Lower back",
        "spine_level": "L4-L5, L5-S1",
        "pain_severity": (6, 8),
        "pain_type": "Dull ache, Stiffness",
        "duration": "2-3 months",
        "numbness": "No",
        "muscle_weakness": "No",
        "nerve_radiation": "No",
        "sleep_disturbance": "Yes",
        "stress_level": "Medium",
        "posture_problem": "Poor sitting posture",
        "triggering_activity": "Sitting for long hours, Lifting heavy objects",
        "movement_limitation": "Difficulty bending forward",
        "diagnosis": "Mechanical Low Back Pain with Lumbar Spondylosis",
        "findings": "Tenderness in lumbar paraspinal muscles. Reduced lumbar range of motion. No neurological deficit.",
        "exam_notes": "Lumbar flexion limited to 60 degrees. Extension painful. SLR negative bilaterally.",
        "scan": "X-ray Lumbar Spine AP/Lateral",
        "therapy": "Chiropractic Adjustment, Soft Tissue Therapy, Postural Correction",
        "chiropractic": "Lumbar spine - L4, L5",
        "soft_tissue": "Myofascial release to lumbar paraspinals, Gluteus medius release",
        "nerve": "None required",
        "muscle": "Core stabilization, Glute bridge",
        "alignment": "Sacroiliac joint mobilization",
        "ayurveda": "Dashmoolarishta 15ml BD",
        "panchakarma": "Kati Basti",
        "oil": "Mahanarayan oil",
        "exercise": "Cat-cow stretch 10 reps, Pelvic tilts 15 reps, Core plank 20s hold",
        "posture_advice": "Use lumbar support. Avoid prolonged sitting. Take breaks every 30 min.",
        "outcome": "Pain reduced. Patient reported improvement in daily activities.",
        "risk_level": "MODERATE",
        "surgery_prob": "LOW",
        "confidence": (0.75, 0.88),
        "recovery": "With regular therapy, 70-80% improvement expected in 4-6 weeks",
        "followup": "Review in 2 weeks. Continue exercises daily.",
    },
    "knee_pain": {
        "pain_areas": "Knee",
        "spine_level": "L3-L4",
        "pain_severity": (5, 7),
        "pain_type": "Dull ache, Stiffness",
        "duration": "1-3 months",
        "numbness": "No",
        "muscle_weakness": "No",
        "nerve_radiation": "No",
        "sleep_disturbance": "No",
        "stress_level": "Medium",
        "posture_problem": "Genu varum",
        "triggering_activity": "Walking, Climbing stairs, Standing for long",
        "movement_limitation": "Difficulty squatting, Stair climbing painful",
        "diagnosis": "Knee Osteoarthritis / Patellofemoral Pain Syndrome",
        "findings": "Mild knee joint effusion. Crepitus on flexion. Medial joint line tenderness.",
        "exam_notes": "Knee flexion 120 degrees with pain at end range. No ligament laxity. McMurray test negative.",
        "scan": "X-ray Knee AP/Lateral weight-bearing",
        "therapy": "Muscle Therapy, Soft Tissue Therapy, Exercise Therapy",
        "chiropractic": "None",
        "soft_tissue": "IT band release, Quadriceps release, Patellar mobilization",
        "nerve": "None required",
        "muscle": "Quadriceps strengthening, Straight leg raises, Terminal knee extension",
        "alignment": "Patellar tracking correction",
        "ayurveda": "Yogaraj guggulu 500mg BD",
        "panchakarma": "Janu Basti",
        "oil": "Ksheerabala oil",
        "exercise": "Quad sets 20 reps, SLR 15 reps, Ankle pumps 20 reps, Stationary cycling 10 min",
        "posture_advice": "Avoid deep squats. Use knee support when walking long distances.",
        "outcome": "Pain reduced. Improved knee range of motion.",
        "risk_level": "LOW",
        "surgery_prob": "LOW",
        "confidence": (0.70, 0.85),
        "recovery": "60-70% improvement expected with 4-6 weeks of conservative therapy",
        "followup": "Review in 3 weeks. Consider quad strengthening progression.",
    },
    "neck_pain": {
        "pain_areas": "Neck, Shoulders",
        "spine_level": "C5-C6, C6-C7",
        "pain_severity": (5, 7),
        "pain_type": "Stiffness, Radiating",
        "duration": "1-2 months",
        "numbness": "No",
        "muscle_weakness": "No",
        "nerve_radiation": "Yes",
        "sleep_disturbance": "Yes",
        "stress_level": "Medium",
        "posture_problem": "Forward head posture",
        "triggering_activity": "Computer work, Mobile phone use, Driving",
        "movement_limitation": "Difficulty turning head, Neck stiffness",
        "diagnosis": "Cervical Spondylosis with Myofascial Pain Syndrome",
        "findings": "Reduced cervical lordosis. Tender trigger points in upper trapezius and levator scapulae. Reduced cervical range of motion.",
        "exam_notes": "Cervical rotation 50 degrees bilaterally. Flexion limited. Spurling test negative.",
        "scan": "X-ray Cervical Spine AP/Lateral/Open mouth",
        "therapy": "Chiropractic Adjustment, Soft Tissue Therapy, Postural Correction",
        "chiropractic": "Cervical spine - C5, C6, C7",
        "soft_tissue": "Upper trapezius release, Levator scapulae trigger point therapy, Suboccipital release",
        "nerve": "Median nerve glide",
        "muscle": "Deep neck flexor strengthening, Scapular retraction",
        "alignment": "Upper thoracic adjustment",
        "ayurveda": "Maharasnadi kwath 20ml BD",
        "panchakarma": "Greeva Basti, Shirodhara",
        "oil": "Ksheerabala oil",
        "exercise": "Chin tucks 15 reps, Upper trap stretch 30s each, Scapular retractions 15 reps",
        "posture_advice": "Raise monitor to eye level. Use headset for calls. Avoid looking down at phone.",
        "outcome": "Reduced neck stiffness. Improved range of motion.",
        "risk_level": "MODERATE",
        "surgery_prob": "LOW",
        "confidence": (0.75, 0.85),
        "recovery": "Good improvement expected in 3-4 weeks with consistent posture correction",
        "followup": "Review in 2 weeks. Continue postural exercises.",
    },
    "slip_disc": {
        "pain_areas": "Lower back, Leg",
        "spine_level": "L4-L5, L5-S1",
        "pain_severity": (7, 9),
        "pain_type": "Sharp, Radiating, Burning",
        "duration": "2-4 months",
        "numbness": "Yes",
        "muscle_weakness": "Yes",
        "nerve_radiation": "Yes",
        "sleep_disturbance": "Yes",
        "stress_level": "High",
        "posture_problem": "Antalgic posture",
        "triggering_activity": "Bending, Lifting, Sitting for long, Coughing/Sneezing",
        "movement_limitation": "Cannot sit for long. Difficulty walking. Unable to bend.",
        "diagnosis": "Lumbar Disc Prolapse with Radiculopathy",
        "findings": "Positive SLR at 40 degrees. Reduced ankle reflex. Sensory loss in affected dermatome. Muscle weakness in corresponding myotome.",
        "exam_notes": "Antalgic gait. Lumbar flexion severely restricted. Crossed SLR positive. Ankle dorsiflexion weak (4/5).",
        "scan": "MRI Lumbar Spine with contrast",
        "therapy": "Chiropractic Adjustment, Nerve Flossing, Traction, Soft Tissue Therapy",
        "chiropractic": "Lumbar spine - L4, L5, Sacrum",
        "soft_tissue": "Piriformis release, Hamstring release, Lumbar paraspinal release",
        "nerve": "Sciatic nerve flossing, Tibial nerve slider exercises",
        "muscle": "Core stabilization, Multifidus activation, Glute medius strengthening",
        "alignment": "Sacroiliac joint adjustment, Pelvic correction",
        "ayurveda": "Dashmoolarishta 20ml BD, Yogaraj guggulu 500mg TDS",
        "panchakarma": "Kati Basti, Sarvanga Abhyanga",
        "oil": "Mahanarayan oil, Dhanwantaram oil",
        "exercise": "Sciatic nerve glide 10 reps, Core plank 20s, Glute bridge 15 reps, Cat-camel 10 reps",
        "posture_advice": "Avoid bending at waist. Use squat technique. Sleep with pillow between knees. Use lumbar roll while sitting.",
        "outcome": "Pain reduced. Improved SLR. Better mobility.",
        "risk_level": "HIGH",
        "surgery_prob": "MODERATE",
        "confidence": (0.80, 0.92),
        "recovery": "60-70% improvement expected in 6-8 weeks with conservative management",
        "followup": "Review after MRI. Consider epidural if no significant improvement in 2 weeks.",
    },
    "sciatica": {
        "pain_areas": "Lower back, Leg, Hip",
        "spine_level": "L4-L5, S1",
        "pain_severity": (7, 8),
        "pain_type": "Radiating, Burning, Shooting",
        "duration": "1-3 months",
        "numbness": "Yes",
        "muscle_weakness": "Yes",
        "nerve_radiation": "Yes",
        "sleep_disturbance": "Yes",
        "stress_level": "High",
        "posture_problem": "Antalgic lean",
        "triggering_activity": "Sitting, Walking, Bending forward",
        "movement_limitation": "Difficulty walking long distances. Cannot sit comfortably.",
        "diagnosis": "Sciatica / Lumbar Radiculopathy",
        "findings": "Positive SLR. Tenderness along sciatic notch. Reduced sensation in lateral foot.",
        "exam_notes": "SLR positive at 50 degrees. Ankle jerk diminished. Toe walking weak on affected side.",
        "scan": "MRI Lumbar Spine",
        "therapy": "Chiropractic Adjustment, Nerve Flossing, Soft Tissue Therapy",
        "chiropractic": "Lumbar spine, SI Joint",
        "soft_tissue": "Piriformis release, Hamstring release, Calf release",
        "nerve": "Sciatic nerve mobilization, Tibial nerve glide",
        "muscle": "Glute activation, Core stabilization",
        "alignment": "Pelvic correction",
        "ayurveda": "Maharasnadi kwath 20ml BD",
        "panchakarma": "Kati Basti",
        "oil": "Mahanarayan oil",
        "exercise": "Piriformis stretch 30s, Sciatic nerve glide 10 reps, Ankle pumps 20 reps",
        "posture_advice": "Avoid prolonged sitting. Use standing desk. Sleep on back with pillow under knees.",
        "outcome": "Reduced leg pain. Improved walking tolerance.",
        "risk_level": "HIGH",
        "surgery_prob": "MODERATE",
        "confidence": (0.78, 0.90),
        "recovery": "50-60% improvement expected in 4-6 weeks",
        "followup": "Review in 1 week. Continue nerve gliding exercises.",
    },
    "shoulder_pain": {
        "pain_areas": "Shoulder, Arm",
        "spine_level": "C5-C6, C6-C7",
        "pain_severity": (5, 7),
        "pain_type": "Dull ache, Sharp on movement",
        "duration": "1-2 months",
        "numbness": "No",
        "muscle_weakness": "Yes",
        "nerve_radiation": "Yes",
        "sleep_disturbance": "Yes",
        "stress_level": "Medium",
        "posture_problem": "Rounded shoulders",
        "triggering_activity": "Overhead activities, Reaching behind, Sleeping on affected side",
        "movement_limitation": "Difficulty raising arm above shoulder. Pain on reaching behind back.",
        "diagnosis": "Frozen Shoulder / Rotator Cuff Tendinopathy",
        "findings": "Restricted shoulder ROM in all planes. Painful arc 60-120 degrees. Tenderness over supraspinatus tendon.",
        "exam_notes": "Shoulder abduction 90 degrees with pain. External rotation limited. Neer test positive.",
        "scan": "Shoulder Ultrasound / X-ray Shoulder AP",
        "therapy": "Soft Tissue Therapy, Exercise Therapy, Postural Correction",
        "chiropractic": "Upper thoracic, AC joint",
        "soft_tissue": "Pectoralis major release, Upper trap release, Supraspinatus release",
        "nerve": "Axillary nerve glide, Radial nerve mobilization",
        "muscle": "Rotator cuff strengthening, Scapular stabilization exercises",
        "alignment": "Glenohumeral joint mobilization, Thoracic spine manipulation",
        "ayurveda": "Yogaraj guggulu 500mg BD",
        "panchakarma": "Abhyanga, Greeva Basti",
        "oil": "Ksheerabala oil",
        "exercise": "Pendulum exercises 2 min, Cane flexion 10 reps, Towel stretch, Wall climbs 10 reps",
        "posture_advice": "Avoid overhead lifting. Sleep on back with arm supported on pillow.",
        "outcome": "Improved shoulder range of motion. Reduced pain on movement.",
        "risk_level": "MODERATE",
        "surgery_prob": "LOW",
        "confidence": (0.72, 0.85),
        "recovery": "60-75% improvement expected in 6-8 weeks with regular therapy",
        "followup": "Review in 3 weeks. Progress stretching and strengthening.",
    },
    "spondylitis": {
        "pain_areas": "Back, Neck, Hips",
        "spine_level": "Lumbar, Cervical",
        "pain_severity": (5, 7),
        "pain_type": "Stiffness, Dull ache",
        "duration": "More than 6 months",
        "numbness": "No",
        "muscle_weakness": "No",
        "nerve_radiation": "No",
        "sleep_disturbance": "Yes",
        "stress_level": "Medium",
        "posture_problem": "Stooped posture",
        "triggering_activity": "Morning stiffness, Inactivity, Cold weather",
        "movement_limitation": "Morning stiffness lasting >30 min. Difficulty in bending.",
        "diagnosis": "Ankylosing Spondylitis / Inflammatory Spondyloarthropathy",
        "findings": "Reduced spinal mobility. Positive Schober test. Tenderness over SI joints. Elevated inflammatory markers.",
        "exam_notes": "Lumbar flexion limited. Chest expansion reduced. Occiput-to-wall test positive.",
        "scan": "X-ray SI Joints, MRI Sacroiliac Joints, HLA-B27",
        "therapy": "Chiropractic Adjustment, Exercise Therapy, Postural Correction",
        "chiropractic": "Thoracic spine, SI Joint, Lumbar spine",
        "soft_tissue": "Paraspinal release, Thoracic soft tissue work",
        "nerve": "None required",
        "muscle": "Spinal extension strengthening, Postural exercises",
        "alignment": "Full spine adjustment",
        "ayurveda": "Maharasnadi kwath 20ml BD, Yogaraj guggulu 500mg BD",
        "panchakarma": "Sarvanga Abhyanga, Swedana, Basti",
        "oil": "Dhanwantaram oil, Mahanarayan oil",
        "exercise": "Spinal extension exercises, Deep breathing exercises, Postural retraining, Swimming recommended",
        "posture_advice": "Sleep on firm mattress. Avoid stooping. Practice upright posture throughout day.",
        "outcome": "Improved spinal mobility. Reduced morning stiffness.",
        "risk_level": "MODERATE",
        "surgery_prob": "LOW",
        "confidence": (0.70, 0.82),
        "recovery": "Chronic condition requiring long-term management. Symptom improvement expected.",
        "followup": "Review monthly. Continue exercise program. Consider rheumatology referral.",
    },
    "paralysis": {
        "pain_areas": "Full body, Legs, Arms",
        "spine_level": "Cervical, Thoracic",
        "pain_severity": (4, 6),
        "pain_type": "Numbness, Weakness",
        "duration": "More than 6 months",
        "numbness": "Yes",
        "muscle_weakness": "Yes",
        "nerve_radiation": "No",
        "sleep_disturbance": "Yes",
        "stress_level": "Very High",
        "posture_problem": "Poor postural control",
        "triggering_activity": "None specific - constant symptoms",
        "movement_limitation": "Significant difficulty with mobility and daily activities",
        "diagnosis": "Paralysis / Hemiparesis / Neurological Deficit",
        "findings": "Reduced muscle strength. Altered sensation. Impaired coordination. Spasticity present.",
        "exam_notes": "Muscle strength 3/5 in affected limbs. Increased tone. Hyperreflexia. Babinski positive.",
        "scan": "MRI Brain and Spine, NCV/EMG studies",
        "therapy": "Muscle Therapy, Exercise Therapy, Nerve Handling",
        "chiropractic": "Full spine gentle adjustment",
        "soft_tissue": "Spastic muscle release, Passive stretching, Range of motion exercises",
        "nerve": "NERVE gliding exercises, Sensory re-education",
        "muscle": "Passive and active-assisted exercises, Functional electrical stimulation",
        "alignment": "Gentle mobilization",
        "ayurveda": "Saraswatarishta 10ml BD, Ashwagandha churna 3gm BD, Brahmi ghrita",
        "panchakarma": "Sarvanga Abhyanga, Shirodhara, Basti, Nasya",
        "oil": "Ksheerabala oil, Bala oil",
        "exercise": "Passive ROM exercises, Bed mobility training, Transfer training, Assisted walking",
        "posture_advice": "Use supportive seating. Pressure relief every 2 hours. Positioning with pillows.",
        "outcome": "Slight improvement in muscle tone. Better range of motion.",
        "risk_level": "CRITICAL",
        "surgery_prob": "LOW",
        "confidence": (0.65, 0.78),
        "recovery": "Long-term rehabilitation. Slow improvement expected over months.",
        "followup": "Weekly follow-up. Multidisciplinary rehabilitation approach.",
    },
    "body_pain": {
        "pain_areas": "Full body, Multiple joints",
        "spine_level": "Generalized",
        "pain_severity": (4, 6),
        "pain_type": "Dull ache, Throbbing",
        "duration": "2-4 months",
        "numbness": "No",
        "muscle_weakness": "Yes",
        "nerve_radiation": "No",
        "sleep_disturbance": "Yes",
        "stress_level": "High",
        "posture_problem": "Poor posture",
        "triggering_activity": "Stress, Overwork, Weather changes",
        "movement_limitation": "Generalized stiffness and fatigue",
        "diagnosis": "Fibromyalgia / Myofascial Pain Syndrome / Generalized Body Ache",
        "findings": "Multiple tender trigger points. Generalized muscle tenderness. Fatigue. Sleep disturbance.",
        "exam_notes": "Tender points in 11 of 18 typical locations. No joint swelling. Normal neurological exam.",
        "scan": "Blood work - ESR, CRP, Vitamin D, Thyroid profile",
        "therapy": "Soft Tissue Therapy, Ayurveda Medicine, Exercise Therapy",
        "chiropractic": "Full spine gentle adjustment",
        "soft_tissue": "Full body myofascial release, Trigger point therapy",
        "nerve": "Relaxation techniques",
        "muscle": "Gentle stretching, Graded exercise program",
        "alignment": "General mobilization",
        "ayurveda": "Ashwagandha churna 3gm BD, Maharasnadi kwath 20ml BD, Triphala at bedtime",
        "panchakarma": "Sarvanga Abhyanga, Shirodhara, Basti",
        "oil": "Bala oil, Dhanwantaram oil",
        "exercise": "Gentle walking 15 min, Deep breathing, Yoga asanas, Progressive relaxation",
        "posture_advice": "Maintain good posture. Ergonomic work setup. Take frequent breaks.",
        "outcome": "Reduced overall body pain. Improved sleep quality.",
        "risk_level": "LOW",
        "surgery_prob": "LOW",
        "confidence": (0.65, 0.80),
        "recovery": "Gradual improvement over 8-12 weeks with lifestyle modification and therapy",
        "followup": "Review every 2 weeks. Continue stress management and graded exercise.",
    },
    "unknown": {
        "pain_areas": "Varies",
        "spine_level": "Not specified",
        "pain_severity": (4, 6),
        "pain_type": "Varies",
        "duration": "Unknown",
        "numbness": "No",
        "muscle_weakness": "No",
        "nerve_radiation": "No",
        "sleep_disturbance": "No",
        "stress_level": "Medium",
        "posture_problem": "Not assessed",
        "triggering_activity": "Not specified",
        "movement_limitation": "Not specified",
        "diagnosis": "Undiagnosed Musculoskeletal Pain - Under Evaluation",
        "findings": "Patient reports pain. detailed examination pending.",
        "exam_notes": "Initial assessment. Further investigation needed.",
        "scan": "Basic blood work and X-ray as needed",
        "therapy": "Symptomatic treatment, Soft Tissue Therapy",
        "chiropractic": "Assessment pending",
        "soft_tissue": "General soft tissue relaxation",
        "nerve": "Assessment pending",
        "muscle": "General stretching",
        "alignment": "Assessment pending",
        "ayurveda": "General health support",
        "panchakarma": "Assessment pending",
        "oil": "Coconut oil",
        "exercise": "General stretching as tolerated",
        "posture_advice": "Maintain good posture. Report specific issues.",
        "outcome": "Initial assessment completed. Further evaluation needed.",
        "risk_level": "LOW",
        "surgery_prob": "LOW",
        "confidence": (0.50, 0.65),
        "recovery": "Pending proper diagnosis",
        "followup": "Schedule detailed examination. Consider diagnostic workup.",
    },
}

CONVERSATION_TEMPLATES = {
    "back_pain": [
        "Doctor: Namaste, aapki lower back pain ke baare mein batayein.\nPatient: Doctor sahab, bahut dard hai peeche. Baithne se aur badh jaata hai.\nDoctor: Yeh pain aapko kab se hai?\nPatient: Kareeb 2-3 mahine se. Pehle halka tha, ab zyada ho gaya.\nDoctor: Kya koi kaam karne se pain trigger hota hai?\nPatient: Haan, jyada der baithne se aur jhukne se pain badh jaata hai.\nDoctor: Hum kuch tests karenge aur aapko exercises batayenge. Regular treatment se aaram milega.",
    ],
    "knee_pain": [
        "Doctor: Kya problem hai aapko?\nPatient: Doctor, mere ghutne mein dard hai. Chadhne-utarne mein bahut takleef hoti hai.\nDoctor: Yeh pain kitne time se hai?\nPatient: Lagbhag 2 mahine se. Pehle thoda tha, ab badh gaya hai.\nDoctor: Kya aapko morning mein stiffness hota hai?\nPatient: Haan, subah uthne par ghutna akda sa ho jaata hai.\nDoctor: Kuch exercises aur medicine se aaram milega. Ghutne ko strong karna hoga.",
    ],
    "neck_pain": [
        "Doctor: Namaste, kaise hain aap?\nPatient: Doctor, gardan mein bahut dard hai. Mobile aur computer par kaam karte hain toh aur badh jaata hai.\nDoctor: Kya aapko kandhe mein bhi dard hai?\nPatient: Haan, right shoulder mein bhi hota hai. Aur kabhi kabhi haath mein bhi jhunjhunehat hoti hai.\nDoctor: Yeh cervical spondylosis ke symptoms hain. Aapko posture sahi karna hoga aur kuch exercises karni hongi.",
    ],
    "slip_disc": [
        "Doctor: Namaste, aapki problem kya hai?\nPatient: Doctor, meri lower back mein bahut tej dard hai aur pair mein numbness hai. Kabhi kabhi pair mein bijli si charti hai.\nDoctor: Yeh pain aapke pair mein bhi jaata hai?\nPatient: Haan, right pair mein directly jaata hai. Main theek se chal bhi nahi paata hoon.\nDoctor: Yeh slip disc ke symptoms hain. Hum MRI recommend karte hain. Tab tak aapko rest lena hoga aur kuch exercises karni hongi.",
    ],
    "sciatica": [
        "Doctor: Kya problem hai?\nPatient: Doctor, meri kamar aur pair mein dard hai. Baithne se aur badh jaata hai.\nDoctor: Pain pair mein kahan tak jaata hai?\nPatient: Right pair mein neeche tak jaata hai. Pair mein numbness bhi hoti hai.\nDoctor: Yeh sciatica hai. Sciatic nerve compress ho gayi hai. Kuch exercises aur treatment se aaram milega.",
    ],
    "shoulder_pain": [
        "Doctor: Namaste, aapki problem?\nPatient: Doctor, mere kandhe mein dard hai. Haath upar nahi utha paata hoon.\nDoctor: Yeh pain kab se hai?\nPatient: Kareeb 1 mahine se. Pehle halka tha, ab haath uthana bhi mushkil ho gaya.\nDoctor: Aapko frozen shoulder ho sakta hai. Isme regular exercises bahut zaroori hain.",
    ],
    "spondylitis": [
        "Doctor: Namaste, kya problem hai aapko?\nPatient: Doctor, meri kamar aur gardan mein akdapan hai. Subah uthne par bahut problem hoti hai.\nDoctor: Morning mein kitni der lagti hai normal feel hone mein?\nPatient: Kareeb 30-40 minute lagte hain theek hone mein.\nDoctor: Yeh inflammatory condition hai. Aapko regular exercise aur treatment ki zaroorat hai.",
    ],
    "paralysis": [
        "Doctor: Namaste, patient kaise hain?\nAttendant: Doctor, unke left side mein weakness hai. Chal nahi paate hain.\nDoctor: Yeh problem kab se hai?\nAttendant: Kareeb 2 mahine se. Pehle thoda improve hua tha but ab vahi hai.\nDoctor: Hum intensive physiotherapy aur Ayurveda treatment karenge. Dheere dheere improvement hoga.",
    ],
    "body_pain": [
        "Doctor: Namaste, kya problem hai?\nPatient: Doctor, mujhe body mein bahut dard rehta hai. Hamesha thakaan si rehti hai. Neend bhi nahi aati theek se.\nDoctor: Yeh pain roj rehta hai?\nPatient: Haan, almost daily. Kaam karte hain toh aur badh jaata hai.\nDoctor: Yeh fibromyalgia type ka pain ho sakta hai. Lifestyle change aur treatment ki zaroorat hai.",
    ],
}

def normalize_gender(val):
    if not val or pd.isna(val):
        return "Other"
    val = str(val).strip().lower()
    if val in ("male", "m"):
        return "Male"
    if val in ("female", "f", "femle", "fe"):
        return "Female"
    return "Other"

def parse_date(val):
    if not val or pd.isna(val):
        return None
    val = str(val).strip()
    try:
        if "-" in val:
            parts = val.split("-")
            if len(parts[0]) == 4:
                d = datetime.strptime(val, "%Y-%m-%d")
                return d.strftime("%d-%m-%Y")
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            d = datetime.strptime(val, fmt)
            return d.strftime("%d-%m-%Y")
        return val
    except Exception:
        return val

def get_disease_template(disease):
    if not disease or pd.isna(disease):
        return DISEASE_TEMPLATES["unknown"]
    d = str(disease).strip().lower()
    if any(k in d for k in ("slip disc", "slip disk", "slipdisk", "slipped disc", "disc prolapse", "disc bulge", "disk bulge", "disc issue", "l4 l5", "l4 & l5", "l5", "l4 /l5")):
        return DISEASE_TEMPLATES["slip_disc"]
    if any(k in d for k in ("sciatica", "saitica", "sietika", "sitica")):
        return DISEASE_TEMPLATES["sciatica"]
    if any(k in d for k in ("knee", "ghutna", "घूटना")):
        return DISEASE_TEMPLATES["knee_pain"]
    if any(k in d for k in ("neck", "cervical", "servical", "cirvacal", "survical")):
        return DISEASE_TEMPLATES["neck_pain"]
    if any(k in d for k in ("shoulder", "sholder", "frojan")):
        return DISEASE_TEMPLATES["shoulder_pain"]
    if any(k in d for k in ("spondylitis", "spondylysis", "as")):
        return DISEASE_TEMPLATES["spondylitis"]
    if any(k in d for k in ("paralysis", "paresis")):
        return DISEASE_TEMPLATES["paralysis"]
    if any(k in d for k in ("body pain", "body ache", "multiple joint pain", "multiple problems", "fibromyalgia", "fever", "inflammation")):
        return DISEASE_TEMPLATES["body_pain"]
    if any(k in d for k in ("back", "spine", "spinal", "lumber", "lumbar", "tailbone", "bek pen", "bake pain", "backbone", "backpain", "bek", "bone")):
        return DISEASE_TEMPLATES["back_pain"]
    return DISEASE_TEMPLATES["unknown"]

def generate_conversation(disease_key, patient_name):
    convs = CONVERSATION_TEMPLATES.get(disease_key, CONVERSATION_TEMPLATES["back_pain"])
    template = random.choice(convs)
    return template

def get_disease_key(disease):
    d = str(disease).strip().lower() if disease and not pd.isna(disease) else ""
    if any(k in d for k in ("slip disc", "slip disk", "slipdisk", "slipped disc", "disc prolapse", "disc bulge", "disk bulge", "disc issue", "l4 l5", "l4 & l5", "l5", "l4 /l5")):
        return "slip_disc"
    if any(k in d for k in ("sciatica", "saitica", "sietika", "sitica")):
        return "sciatica"
    if any(k in d for k in ("knee", "ghutna", "घूटना")):
        return "knee_pain"
    if any(k in d for k in ("neck", "cervical", "servical", "cirvacal", "survical")):
        return "neck_pain"
    if any(k in d for k in ("shoulder", "sholder", "frojan")):
        return "shoulder_pain"
    if any(k in d for k in ("spondylitis", "spondylysis", "as")):
        return "spondylitis"
    if any(k in d for k in ("paralysis", "paresis")):
        return "paralysis"
    if any(k in d for k in ("body pain", "body ache", "multiple joint pain", "multiple problems", "fibromyalgia", "fever", "inflammation")):
        return "body_pain"
    if any(k in d for k in ("back", "spine", "spinal", "lumber", "lumbar", "tailbone", "bek pen", "bake pain", "backbone", "backpain", "bek", "bone")):
        return "back_pain"
    return "unknown"


OUTCOME_VARIANTS = {
    "improving": [
        "Significant improvement this session. Pain reduced by 60%. Patient reporting better sleep and mobility.",
        "Good progress. Continuing with same treatment protocol. Patient compliant with home exercises.",
        "Moderate improvement. Adjusted technique for better results. Patient motivated.",
        "Steady progress. Range of motion improving. Pain levels decreasing gradually.",
        "Positive response to treatment. Reduced medication dependency. Daily activities improving.",
    ],
    "stable": [
        "Condition stabilizing. Pain levels consistent. Continue current management plan.",
        "No significant change this session. Maintaining current protocol.",
        "Slight improvement in symptoms. Patient advised to continue exercises regularly.",
        "Symptoms managed well. Focusing on maintenance and prevention.",
        "Consistent progress. Patient reports better quality of daily life.",
    ],
    "followup": [
        "Post-followup assessment. Good compliance with treatment plan. Continue maintenance care.",
        "Routine follow-up. Patient maintaining well. Preventive advice given.",
        "Follow-up visit. Minor adjustments made. Patient satisfied with progress.",
        "Periodic assessment. Overall improvement sustained. Continue preventive exercises.",
    ],
}

MOBILITY_LEVELS = ["No Change", "Slight Improvement", "Improved", "Significantly Improved"]
SLEEP_LEVELS = ["No Change", "Slight Improvement", "Improved", "Significantly Improved"]
NUMBNESS_LEVELS = ["No Change", "Slight Improvement", "Improved"]

PATIENT_FEEDBACKS = [
    "Bahut aaram hai, pehle se bohot better hoon.",
    "Pain almost chala gaya hai. Thank you doctor.",
    "Thoda pain hai abhi bhi lekin pehle jaisa nahi hai.",
    "Exercises regular kar raha hoon. Improvement ho raha hai.",
    "Pehle se better feel ho raha hai. Neend bhi achi aa rahi hai.",
    "Treatment se bahut fark pada hai. Continue karna chahta hoon.",
    "Slowly slowly theek ho raha hoon. Kuch dino mein aur aaram hoga.",
    "Ab main apne daily kaam kar pa raha hoon. Thank you.",
    "Pain kam hua hai but completely nahi gaya hai.",
    "Sessions helpful hain. Mobility improve hui hai.",
]

PRACTITIONER_REMARKS = [
    "Good response to treatment. Continue current protocol.",
    "Patient compliant with home exercises. Progressing as expected.",
    "Moderate improvement noted. Adjusting treatment for continued gains.",
    "Satisfactory progress. Recommend increasing exercise intensity.",
    "Excellent improvement. Moving to maintenance phase.",
    "Patient motivated and consistent. Good clinical outcome.",
    "Mild improvement this session. Modified approach for better results.",
    "Steady progress. Plan to reduce frequency to once weekly.",
    "Good range of motion achieved. Focusing on strength now.",
    "Patient reported significant reduction in pain score.",
]

PAIN_TYPES_VARIANTS = [
    "Sharp, Radiating, Burning",
    "Dull ache, Stiffness, Throbbing",
    "Radiating, Shooting, Tingling",
    "Constant ache, Intermittent sharp pain",
    "Burning sensation, Numbness, Weakness",
    "Stiffness, Reduced mobility, Dull pain",
]

TRIGGER_VARIANTS = [
    "Prolonged sitting, Bending, Lifting",
    "Standing for long hours, Walking, Climbing stairs",
    "Computer work, Driving, Looking down at phone",
    "Overhead activities, Reaching, Sleeping on affected side",
    "Morning stiffness, Cold weather, Inactivity",
    "Sudden movement, Twisting, Coughing/Sneezing",
]

MOVEMENT_VARIANTS = [
    "Difficulty bending forward and sitting for long periods",
    "Reduced range of motion in daily activities",
    "Pain on specific movements, Limited flexibility",
    "Difficulty with overhead activities and reaching behind",
    "Morning stiffness lasting 20-30 minutes",
    "Unable to perform routine tasks without discomfort",
]


def make_datetime(base_str: str, days_offset: int, hour: int = None, minute: int = None):
    parts = base_str.split("-")
    try:
        base = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
    except:
        base = datetime(2026, 1, 15)
    dt = base + timedelta(days=days_offset)
    h = random.randint(9, 16) if hour is None else hour
    m = random.randint(0, 59) if minute is None else minute
    return dt.strftime("%d-%m-%Y"), f"{dt.strftime('%d-%m-%Y')} {h:02d}:{m:02d}"


def parse_visit_date(row, idx):
    raw = row.get("Date of Visiting")
    if raw and not pd.isna(raw):
        parsed = parse_date(raw)
        if parsed and "-" in parsed:
            try:
                datetime.strptime(parsed[:10], "%d-%m-%Y")
                return parsed[:10]
            except:
                pass
    return f"{random.randint(1, 28):02d}-{random.randint(1, 12):02d}-2026"


def seed_database():
    init_db()
    db = SessionLocal()

    existing = db.query(Patient).count()
    if existing > 0:
        db.close()
        return

    if not os.path.exists(DATA_FILE):
        print(f"data.xlsx not found at {DATA_FILE}")
        db.close()
        return

    try:
        df = pd.read_excel(DATA_FILE)
    except ImportError:
        print("openpyxl not available. Install with: pip install openpyxl")
        db.close()
        return
    except Exception as e:
        print(f"Error reading data.xlsx: {e}")
        db.close()
        return

    print(f"Loading {len(df)} patients from data.xlsx...")
    patient_count = 0
    total_consultations = 0
    total_assessments = 0
    total_treatments = 0
    total_conversations = 0
    total_ai_outputs = 0
    total_progress = 0
    existing_patients_map = {}

    for idx, row in df.iterrows():
        try:
            pname = str(row.get("Patient Name", "")).strip() if not pd.isna(row.get("Patient Name", "")) else ""
            if not pname:
                continue

            mobile = str(row.get("Phone number", "")).strip()
            mobile = re.sub(r"\D", "", mobile) if mobile != "nan" else ""
            if not mobile or len(mobile) < 10:
                mobile = f"987654{1000 + idx:04d}"

            alternate = str(row.get("Alternate phone Number", "")).strip()
            alternate = re.sub(r"\D", "", alternate) if alternate and alternate != "nan" else ""

            disease = str(row.get("Disease", "")).strip() if not pd.isna(row.get("Disease", "")) else ""
            template = get_disease_template(disease)
            disease_key = get_disease_key(disease)

            patient_key = (pname.lower().strip(), mobile)
            if patient_key in existing_patients_map:
                patient = existing_patients_map[patient_key]
                is_new_patient = False
            else:
                is_new_patient = True
                age_val = row.get("Age", 30)
                try:
                    age = int(float(age_val))
                except:
                    age = 30

                height = random.choice([155, 160, 165, 168, 170, 172, 175, 178, 180])
                weight = random.randint(55, 95)
                bmi = calculate_bmi(height, weight)
                gender = normalize_gender(row.get("Gender", "Other"))

                patient = Patient(
                    full_name=pname,
                    age=age,
                    gender=gender,
                    dob=parse_date(row.get("Date of Birth")),
                    mobile=mobile,
                    email=str(row.get("Email", "")).strip() if not pd.isna(row.get("Email", "")) else None,
                    occupation=str(row.get("Occupation", "")).strip() if not pd.isna(row.get("Occupation", "")) else None,
                    height=float(height),
                    weight=float(weight),
                    bmi=bmi,
                    address=str(row.get("Address", "")).strip() if not pd.isna(row.get("Address", "")) else None,
                    lifestyle=random.choice(["Sedentary", "Moderately Active", "Active"]),
                    smoking_alcohol=random.choice(["No", "Occasional", "Regular", "No", "No"]),
                    existing_diseases=random.choice(["None", "None", "None", "Hypertension", "Diabetes", "Thyroid", "Hypertension, Diabetes"]),
                    previous_spine_surgery=random.choice(["No", "No", "No", "No", "Yes"]),
                    emergency_contact=alternate if alternate else mobile,
                )
                db.add(patient)
                db.flush()
                existing_patients_map[patient_key] = patient
                patient_count += 1

            base_date_str = parse_visit_date(row, idx)
            num_consultations = random.choices([2, 3, 1], weights=[5, 3, 2])[0]
            initial_severity = random.randint(template["pain_severity"][0], template["pain_severity"][1])

            for consult_num in range(num_consultations):
                days_offset = consult_num * random.randint(14, 28)
                date_only, consult_datetime = make_datetime(base_date_str, days_offset)

                severity = max(1, initial_severity - random.randint(0, consult_num * 2))
                severity = min(severity, initial_severity)

                followup_dt = datetime.strptime(date_only, "%d-%m-%Y") + timedelta(days=random.randint(10, 21))
                followup = followup_dt.strftime("%d-%m-%Y")

                consult_stage = "initial" if consult_num == 0 else "followup" if consult_num == num_consultations - 1 else "intermediate"
                stage_key = "improving" if consult_stage != "initial" else "stable"
                if consult_stage == "followup":
                    stage_key = "followup"

                assessment = PainAssessment(
                    patient_id=patient.patient_id,
                    main_problem=disease,
                    pain_areas=template["pain_areas"],
                    spine_level=template["spine_level"],
                    pain_severity=severity,
                    pain_type=random.choice(PAIN_TYPES_VARIANTS) if consult_num > 0 else template["pain_type"],
                    duration=template["duration"],
                    triggering_activity=random.choice(TRIGGER_VARIANTS) if consult_num > 0 else template["triggering_activity"],
                    movement_limitation=random.choice(MOVEMENT_VARIANTS) if consult_num > 0 else template["movement_limitation"],
                    numbness=template["numbness"],
                    muscle_weakness=template["muscle_weakness"],
                    nerve_radiation=template["nerve_radiation"],
                    sleep_disturbance=template["sleep_disturbance"],
                    posture_problem=template["posture_problem"],
                    stress_level=template["stress_level"],
                )
                db.add(assessment)
                total_assessments += 1

                findings_variant = template["findings"]
                if consult_num > 0:
                    findings_variant += f" Follow-up: Pain reduced from {initial_severity}/10 to {severity}/10."

                consultation = Consultation(
                    patient_id=patient.patient_id,
                    doctor_name="Dr. Rajat",
                    specialization="Chiropractic & Spine Specialist",
                    consultation_datetime=consult_datetime,
                    chief_complaint=disease,
                    clinical_findings=findings_variant,
                    examination_notes=template["exam_notes"],
                    preliminary_diagnosis=template["diagnosis"],
                    recommended_scan=template["scan"] if consult_num == 0 else "Review previous reports",
                    followup_date=followup,
                )
                db.add(consultation)
                db.flush()
                total_consultations += 1

                outcome_options = OUTCOME_VARIANTS[stage_key]
                treatment = Treatment(
                    consultation_id=consultation.consultation_id,
                    therapy_types=template["therapy"],
                    chiropractic_area=template["chiropractic"],
                    soft_tissue_therapy=template["soft_tissue"],
                    nerve_handling=template["nerve"],
                    muscle_therapy=template["muscle"],
                    bone_alignment=template["alignment"],
                    ayurveda_medicine=template["ayurveda"],
                    panchakarma_type=template["panchakarma"],
                    oil_used=template["oil"],
                    home_exercise=template["exercise"],
                    posture_advice=template["posture_advice"],
                    session_duration=random.choice([30, 40, 45, 60]),
                    session_outcome=random.choice(outcome_options),
                )
                db.add(treatment)
                total_treatments += 1

                transcript = generate_conversation(disease_key, pname)
                emotional_states = ["Anxious", "In pain", "Calm", "Hopeful", "Concerned"]
                if consult_num == num_consultations - 1:
                    emotional_states = ["Calm", "Hopeful", "Satisfied"]
                conversation = Conversation(
                    consultation_id=consultation.consultation_id,
                    source_type=random.choice(["manual", "manual", "audio"]),
                    transcript=transcript,
                    language="Hindi + English",
                    speaker_separation=f"Doctor: Dr. Rajat, Patient: {pname}",
                    emotional_state=random.choice(emotional_states),
                    pain_keywords=f"{disease}, {template['pain_areas']}, pain, severity {severity}/10",
                )
                db.add(conversation)
                db.flush()
                total_conversations += 1

                ai_output = AIOutput(
                    conversation_id=conversation.conversation_id,
                    ai_summary=f"{age}-year-old {gender} with {disease}. "
                               f"Pain severity {severity}/10. {template['diagnosis']}. "
                               f"Visit {consult_num + 1} of {num_consultations}. "
                               f"Recommended: {template['therapy']}.",
                    extracted_symptoms=f"{template['pain_areas']} pain, {template['pain_type'].lower()}",
                    body_area_detected=template["pain_areas"],
                    possible_condition=template["diagnosis"],
                    predicted_pain_severity=severity,
                    recommended_therapy=template["therapy"],
                    recommended_tests=template["scan"] if consult_num == 0 else "Follow-up assessment",
                    suggested_ayurveda=template["panchakarma"],
                    risk_level=template["risk_level"],
                    surgery_probability=template["surgery_prob"],
                    recovery_prediction=template["recovery"],
                    followup_suggestion=template["followup"],
                    confidence_score=round(random.uniform(template["confidence"][0], template["confidence"][1]), 2),
                    raw_json="{}",
                )
                db.add(ai_output)
                total_ai_outputs += 1

            try:
                base_dt = datetime.strptime(base_date_str, "%d-%m-%Y")
            except:
                base_dt = datetime(2026, 1, 15)

            num_sessions = random.randint(4, 6)
            progress_severity = initial_severity
            for session_num in range(1, num_sessions + 1):
                session_date = base_dt + timedelta(days=(session_num - 1) * 7)
                session_date_str = session_date.strftime("%d-%m-%Y")

                prev_score = progress_severity
                improvement = random.randint(0, min(2, progress_severity))
                current_score = max(0, progress_severity - improvement)
                progress_severity = current_score

                mobility_idx = min(3, session_num // 2)
                sleep_idx = min(3, session_num // 2)
                numbness_idx = min(2, session_num // 2)

                progress = ProgressTracking(
                    patient_id=patient.patient_id,
                    session_number=session_num,
                    progress_date=session_date_str,
                    previous_pain_score=prev_score,
                    current_pain_score=current_score,
                    mobility_improvement=MOBILITY_LEVELS[mobility_idx],
                    sleep_improvement=SLEEP_LEVELS[sleep_idx],
                    numbness_improvement=NUMBNESS_LEVELS[numbness_idx] if template["numbness"] == "Yes" else None,
                    patient_feedback=random.choice(PATIENT_FEEDBACKS),
                    practitioner_remark=random.choice(PRACTITIONER_REMARKS),
                )
                db.add(progress)
                total_progress += 1

            if patient_count % 50 == 0:
                db.commit()
                print(f"  Seeded {patient_count} patients...")

        except Exception as e:
            print(f"  Error on row {idx}: {e}")
            traceback.print_exc()
            continue

    db.commit()
    db.close()
    print(f"\nSeeded {patient_count} patients with full clinical data!")
    print(f"  - Pain assessments: {total_assessments}")
    print(f"  - Consultations: {total_consultations}")
    print(f"  - Treatments: {total_treatments}")
    print(f"  - Conversations: {total_conversations}")
    print(f"  - AI outputs: {total_ai_outputs}")
    print(f"  - Progress entries: {total_progress}")


if __name__ == "__main__":
    seed_database()
