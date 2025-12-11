"""
Fitness & Gym Membership Management System
CMPE 351 - Database Systems Project
Author: Nehir
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import os

# ========================================
# DATABASE SETUP & CONNECTION
# ========================================

def get_connection():
    """Create and return database connection"""
    conn = sqlite3.connect('gym_management.db', check_same_thread=False)
    return conn

def create_tables():
    """Create all database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table 1: MEMBERS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Members (
        Member_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        First_Name TEXT NOT NULL,
        Last_Name TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Phone TEXT NOT NULL,
        Date_of_Birth DATE NOT NULL,
        Join_Date DATE NOT NULL,
        Status TEXT CHECK(Status IN ('Active', 'Inactive')) DEFAULT 'Active'
    )
    ''')
    
    # Table 2: MEMBERSHIP_PLANS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Membership_Plans (
        Plan_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Plan_Name TEXT NOT NULL,
        Duration_Months INTEGER NOT NULL,
        Price REAL NOT NULL CHECK(Price >= 0),
        Benefits_Description TEXT
    )
    ''')
    
    # Table 3: MEMBER_MEMBERSHIPS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Member_Memberships (
        Membership_Record_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Member_ID INTEGER NOT NULL,
        Plan_ID INTEGER NOT NULL,
        Start_Date DATE NOT NULL,
        End_Date DATE NOT NULL,
        Payment_Status TEXT CHECK(Payment_Status IN ('Paid', 'Pending', 'Expired')) DEFAULT 'Pending',
        Is_Active INTEGER CHECK(Is_Active IN (0, 1)) DEFAULT 1,
        FOREIGN KEY (Member_ID) REFERENCES Members(Member_ID) ON DELETE CASCADE,
        FOREIGN KEY (Plan_ID) REFERENCES Membership_Plans(Plan_ID) ON DELETE RESTRICT
    )
    ''')
    
    # Table 4: TRAINERS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Trainers (
        Trainer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        First_Name TEXT NOT NULL,
        Last_Name TEXT NOT NULL,
        Specialization TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Phone TEXT NOT NULL,
        Hire_Date DATE NOT NULL
    )
    ''')
    
    # Table 5: CLASSES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Classes (
        Class_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Class_Name TEXT NOT NULL,
        Class_Type TEXT NOT NULL,
        Trainer_ID INTEGER NOT NULL,
        Schedule_Day TEXT CHECK(Schedule_Day IN ('Monday', 'Tuesday', 'Wednesday', 
                                                   'Thursday', 'Friday', 'Saturday', 'Sunday')),
        Schedule_Time TEXT NOT NULL,
        Duration_Minutes INTEGER NOT NULL CHECK(Duration_Minutes > 0),
        Max_Capacity INTEGER NOT NULL CHECK(Max_Capacity > 0),
        FOREIGN KEY (Trainer_ID) REFERENCES Trainers(Trainer_ID) ON DELETE RESTRICT
    )
    ''')
    
    # Table 6: CLASS_BOOKINGS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Class_Bookings (
        Booking_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Member_ID INTEGER NOT NULL,
        Class_ID INTEGER NOT NULL,
        Booking_Date DATE NOT NULL,
        Attendance_Status TEXT CHECK(Attendance_Status IN 
                                    ('Booked', 'Attended', 'Cancelled', 'No-Show')) DEFAULT 'Booked',
        FOREIGN KEY (Member_ID) REFERENCES Members(Member_ID) ON DELETE CASCADE,
        FOREIGN KEY (Class_ID) REFERENCES Classes(Class_ID) ON DELETE CASCADE,
        UNIQUE(Member_ID, Class_ID, Booking_Date)
    )
    ''')
    
    conn.commit()
    conn.close()

def insert_sample_data():
    """Insert sample data into all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM Members")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # Data already inserted
    
    # Sample Members (5+)
    members = [
        ('John', 'Doe', 'john.doe@email.com', '555-0101', '1990-05-15', '2024-01-10', 'Active'),
        ('Jane', 'Smith', 'jane.smith@email.com', '555-0102', '1988-08-22', '2024-02-15', 'Active'),
        ('Michael', 'Johnson', 'michael.j@email.com', '555-0103', '1995-03-10', '2024-01-20', 'Active'),
        ('Emily', 'Davis', 'emily.davis@email.com', '555-0104', '1992-11-30', '2024-03-01', 'Active'),
        ('Robert', 'Wilson', 'robert.w@email.com', '555-0105', '1985-07-18', '2023-12-05', 'Active'),
        ('Sarah', 'Brown', 'sarah.b@email.com', '555-0106', '1998-02-14', '2024-04-10', 'Inactive'),
    ]
    cursor.executemany('INSERT INTO Members (First_Name, Last_Name, Email, Phone, Date_of_Birth, Join_Date, Status) VALUES (?, ?, ?, ?, ?, ?, ?)', members)
    
    # Sample Membership Plans (5+)
    plans = [
        ('Basic Monthly', 1, 50.00, 'Gym access only'),
        ('Basic Annual', 12, 500.00, 'Gym access only - 2 months free'),
        ('Premium Monthly', 1, 80.00, 'Gym + unlimited classes'),
        ('Premium Annual', 12, 850.00, 'Gym + unlimited classes - 2 months free'),
        ('VIP Monthly', 1, 150.00, 'Gym + classes + 4 PT sessions'),
        ('VIP Annual', 12, 1600.00, 'Gym + classes + 4 PT sessions/month'),
    ]
    cursor.executemany('INSERT INTO Membership_Plans (Plan_Name, Duration_Months, Price, Benefits_Description) VALUES (?, ?, ?, ?)', plans)
    
    # Sample Member Memberships (5+)
    memberships = [
        (1, 3, '2024-01-10', '2024-02-10', 'Paid', 1),
        (2, 4, '2024-02-15', '2025-02-15', 'Paid', 1),
        (3, 1, '2024-01-20', '2024-02-20', 'Paid', 1),
        (4, 5, '2024-03-01', '2024-04-01', 'Paid', 1),
        (5, 2, '2023-12-05', '2024-12-05', 'Paid', 1),
        (6, 1, '2024-04-10', '2024-05-10', 'Expired', 0),
    ]
    cursor.executemany('INSERT INTO Member_Memberships (Member_ID, Plan_ID, Start_Date, End_Date, Payment_Status, Is_Active) VALUES (?, ?, ?, ?, ?, ?)', memberships)
    
    # Sample Trainers (5+)
    trainers = [
        ('Alex', 'Martinez', 'Yoga', 'alex.martinez@gym.com', '555-1001', '2023-06-01'),
        ('Lisa', 'Anderson', 'CrossFit', 'lisa.anderson@gym.com', '555-1002', '2023-07-15'),
        ('David', 'Thompson', 'Pilates', 'david.thompson@gym.com', '555-1003', '2023-08-20'),
        ('Nina', 'Garcia', 'Spinning', 'nina.garcia@gym.com', '555-1004', '2023-09-10'),
        ('Chris', 'Lee', 'Zumba', 'chris.lee@gym.com', '555-1005', '2024-01-05'),
        ('Emma', 'Taylor', 'Personal Training', 'emma.taylor@gym.com', '555-1006', '2022-03-15'),
    ]
    cursor.executemany('INSERT INTO Trainers (First_Name, Last_Name, Specialization, Email, Phone, Hire_Date) VALUES (?, ?, ?, ?, ?, ?)', trainers)
    
    # Sample Classes (5+)
    classes = [
        ('Morning Yoga', 'Yoga', 1, 'Monday', '08:00', 60, 20),
        ('CrossFit Extreme', 'CrossFit', 2, 'Tuesday', '18:00', 45, 15),
        ('Pilates Core', 'Pilates', 3, 'Wednesday', '10:00', 50, 25),
        ('Spinning Cycle', 'Spinning', 4, 'Thursday', '19:00', 45, 30),
        ('Zumba Dance', 'Zumba', 5, 'Friday', '17:00', 60, 35),
        ('Evening Yoga', 'Yoga', 1, 'Saturday', '18:00', 60, 20),
        ('Weekend CrossFit', 'CrossFit', 2, 'Sunday', '10:00', 45, 15),
    ]
    cursor.executemany('INSERT INTO Classes (Class_Name, Class_Type, Trainer_ID, Schedule_Day, Schedule_Time, Duration_Minutes, Max_Capacity) VALUES (?, ?, ?, ?, ?, ?, ?)', classes)
    
    # Sample Class Bookings (5+)
    bookings = [
        (1, 1, '2024-11-18', 'Attended'),
        (1, 2, '2024-11-19', 'Attended'),
        (2, 3, '2024-11-20', 'Booked'),
        (3, 1, '2024-11-18', 'Attended'),
        (4, 5, '2024-11-22', 'Booked'),
        (5, 4, '2024-11-21', 'No-Show'),
        (2, 5, '2024-11-22', 'Booked'),
    ]
    cursor.executemany('INSERT INTO Class_Bookings (Member_ID, Class_ID, Booking_Date, Attendance_Status) VALUES (?, ?, ?, ?)', bookings)
    
    conn.commit()
    conn.close()

# ========================================
# CRUD OPERATIONS
# ========================================

def insert_member(first_name, last_name, email, phone, dob, join_date, status):
    """Insert a new member"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Members (First_Name, Last_Name, Email, Phone, Date_of_Birth, Join_Date, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, phone, dob, join_date, status))
        conn.commit()
        conn.close()
        return True, "Member added successfully!"
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, f"Error: {str(e)}"

def insert_membership_plan(plan_name, duration, price, benefits):
    """Insert a new membership plan"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Membership_Plans (Plan_Name, Duration_Months, Price, Benefits_Description)
            VALUES (?, ?, ?, ?)
        ''', (plan_name, duration, price, benefits))
        conn.commit()
        conn.close()
        return True, "Membership plan added successfully!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def insert_trainer(first_name, last_name, specialization, email, phone, hire_date):
    """Insert a new trainer"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Trainers (First_Name, Last_Name, Specialization, Email, Phone, Hire_Date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, specialization, email, phone, hire_date))
        conn.commit()
        conn.close()
        return True, "Trainer added successfully!"
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, f"Error: {str(e)}"

def insert_class(class_name, class_type, trainer_id, schedule_day, schedule_time, duration, capacity):
    """Insert a new class"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Classes (Class_Name, Class_Type, Trainer_ID, Schedule_Day, Schedule_Time, Duration_Minutes, Max_Capacity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (class_name, class_type, trainer_id, schedule_day, schedule_time, duration, capacity))
        conn.commit()
        conn.close()
        return True, "Class added successfully!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def insert_booking(member_id, class_id, booking_date, status):
    """Insert a new class booking"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Class_Bookings (Member_ID, Class_ID, Booking_Date, Attendance_Status)
            VALUES (?, ?, ?, ?)
        ''', (member_id, class_id, booking_date, status))
        conn.commit()
        conn.close()
        return True, "Booking created successfully!"
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, f"Error: Member already has a booking for this class on this date"

def delete_record(table_name, id_column, record_id):
    """Delete a record from specified table"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'DELETE FROM {table_name} WHERE {id_column} = ?', (record_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        if rows_affected > 0:
            return True, f"Record deleted successfully!"
        else:
            return False, "Record not found!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def update_member(member_id, first_name, last_name, email, phone, status):
    """Update member information"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE Members 
            SET First_Name = ?, Last_Name = ?, Email = ?, Phone = ?, Status = ?
            WHERE Member_ID = ?
        ''', (first_name, last_name, email, phone, status, member_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        if rows_affected > 0:
            return True, "Member updated successfully!"
        else:
            return False, "Member not found!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def update_class(class_id, class_name, schedule_day, schedule_time, max_capacity):
    """Update class information"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE Classes 
            SET Class_Name = ?, Schedule_Day = ?, Schedule_Time = ?, Max_Capacity = ?
            WHERE Class_ID = ?
        ''', (class_name, schedule_day, schedule_time, max_capacity, class_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        if rows_affected > 0:
            return True, "Class updated successfully!"
        else:
            return False, "Class not found!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def update_booking_status(booking_id, new_status):
    """Update booking attendance status"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE Class_Bookings 
            SET Attendance_Status = ?
            WHERE Booking_ID = ?
        ''', (new_status, booking_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        if rows_affected > 0:
            return True, "Booking status updated successfully!"
        else:
            return False, "Booking not found!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

# ========================================
# JOIN QUERIES
# ========================================

def get_member_memberships_join():
    """JOIN: Get members with their active membership plans"""
    conn = get_connection()
    query = '''
    SELECT 
        m.Member_ID,
        m.First_Name || ' ' || m.Last_Name AS Member_Name,
        m.Email,
        mp.Plan_Name,
        mp.Price,
        mm.Start_Date,
        mm.End_Date,
        mm.Payment_Status,
        CASE WHEN mm.Is_Active = 1 THEN 'Active' ELSE 'Inactive' END AS Status
    FROM Members m
    JOIN Member_Memberships mm ON m.Member_ID = mm.Member_ID
    JOIN Membership_Plans mp ON mm.Plan_ID = mp.Plan_ID
    ORDER BY m.Member_ID
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_class_schedule_join():
    """JOIN: Get class schedule with trainer information"""
    conn = get_connection()
    query = '''
    SELECT 
        c.Class_ID,
        c.Class_Name,
        c.Class_Type,
        t.First_Name || ' ' || t.Last_Name AS Trainer_Name,
        t.Specialization,
        c.Schedule_Day,
        c.Schedule_Time,
        c.Duration_Minutes,
        c.Max_Capacity
    FROM Classes c
    JOIN Trainers t ON c.Trainer_ID = t.Trainer_ID
    ORDER BY 
        CASE c.Schedule_Day
            WHEN 'Monday' THEN 1
            WHEN 'Tuesday' THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday' THEN 4
            WHEN 'Friday' THEN 5
            WHEN 'Saturday' THEN 6
            WHEN 'Sunday' THEN 7
        END,
        c.Schedule_Time
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_member_bookings_join():
    """JOIN: Get member bookings with class and trainer details"""
    conn = get_connection()
    query = '''
    SELECT 
        m.First_Name || ' ' || m.Last_Name AS Member_Name,
        c.Class_Name,
        c.Class_Type,
        t.First_Name || ' ' || t.Last_Name AS Trainer_Name,
        c.Schedule_Day,
        c.Schedule_Time,
        cb.Booking_Date,
        cb.Attendance_Status
    FROM Class_Bookings cb
    JOIN Members m ON cb.Member_ID = m.Member_ID
    JOIN Classes c ON cb.Class_ID = c.Class_ID
    JOIN Trainers t ON c.Trainer_ID = t.Trainer_ID
    ORDER BY cb.Booking_Date DESC, m.Last_Name
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_trainer_workload_join():
    """JOIN: Get trainer workload (number of classes per trainer)"""
    conn = get_connection()
    query = '''
    SELECT 
        t.Trainer_ID,
        t.First_Name || ' ' || t.Last_Name AS Trainer_Name,
        t.Specialization,
        COUNT(c.Class_ID) AS Number_of_Classes,
        GROUP_CONCAT(c.Class_Name, ', ') AS Classes_Teaching
    FROM Trainers t
    LEFT JOIN Classes c ON t.Trainer_ID = c.Trainer_ID
    GROUP BY t.Trainer_ID, t.First_Name, t.Last_Name, t.Specialization
    ORDER BY Number_of_Classes DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ========================================
# UTILITY FUNCTIONS
# ========================================

def get_all_records(table_name):
    """Get all records from a table"""
    conn = get_connection()
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
    conn.close()
    return df

def get_members():
    """Get all members"""
    return get_all_records('Members')

def get_trainers():
    """Get all trainers"""
    return get_all_records('Trainers')

def get_classes():
    """Get all classes"""
    return get_all_records('Classes')

def get_bookings():
    """Get all bookings"""
    return get_all_records('Class_Bookings')

def get_membership_plans():
    """Get all membership plans"""
    return get_all_records('Membership_Plans')

# ========================================
# STREAMLIT UI
# ========================================

def main():
    st.set_page_config(
        page_title="Gym Management System",
        page_icon="💪",
        layout="wide"
    )
    
    # Initialize database
    create_tables()
    insert_sample_data()
    
    # Header
    st.title("💪 Fitness & Gym Membership Management System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio(
        "Select Operation:",
        ["🏠 Home", "➕ Insert Data", "❌ Delete Data", "✏️ Update Data", "🔍 JOIN Queries", "📊 View Tables"]
    )
    
    # ========================================
    # HOME PAGE
    # ========================================
    if menu == "🏠 Home":
        st.header("Welcome to Gym Management System")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            member_count = len(get_members())
            st.metric("Total Members", member_count)
        
        with col2:
            trainer_count = len(get_trainers())
            st.metric("Total Trainers", trainer_count)
        
        with col3:
            class_count = len(get_classes())
            st.metric("Total Classes", class_count)
        
        st.markdown("---")
        st.subheader("System Features")
        st.write("✅ Member Management")
        st.write("✅ Membership Plans")
        st.write("✅ Trainer Management")
        st.write("✅ Class Scheduling")
        st.write("✅ Class Booking System")
        st.write("✅ Comprehensive Reporting")
    
    # ========================================
    # INSERT DATA
    # ========================================
    elif menu == "➕ Insert Data":
        st.header("Insert New Data")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Member", "📋 Membership Plan", "🏋️ Trainer", "📅 Class", "🎫 Booking"])
        
        # Insert Member
        with tab1:
            st.subheader("Add New Member")
            with st.form("insert_member_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name*")
                    last_name = st.text_input("Last Name*")
                    email = st.text_input("Email*")
                with col2:
                    phone = st.text_input("Phone*")
                    dob = st.date_input("Date of Birth*")
                    join_date = st.date_input("Join Date*", value=date.today())
                
                status = st.selectbox("Status", ["Active", "Inactive"])
                
                submitted = st.form_submit_button("Add Member")
                if submitted:
                    if first_name and last_name and email and phone:
                        success, message = insert_member(first_name, last_name, email, phone, dob, join_date, status)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all required fields!")
        
        # Insert Membership Plan
        with tab2:
            st.subheader("Add New Membership Plan")
            with st.form("insert_plan_form"):
                plan_name = st.text_input("Plan Name*")
                col1, col2 = st.columns(2)
                with col1:
                    duration = st.number_input("Duration (Months)*", min_value=1, max_value=24, value=1)
                with col2:
                    price = st.number_input("Price ($)*", min_value=0.0, value=50.0, step=10.0)
                benefits = st.text_area("Benefits Description")
                
                submitted = st.form_submit_button("Add Plan")
                if submitted:
                    if plan_name:
                        success, message = insert_membership_plan(plan_name, duration, price, benefits)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all required fields!")
        
        # Insert Trainer
        with tab3:
            st.subheader("Add New Trainer")
            with st.form("insert_trainer_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name*")
                    last_name = st.text_input("Last Name*")
                    specialization = st.selectbox("Specialization*", 
                                                 ["Yoga", "CrossFit", "Pilates", "Spinning", "Zumba", "Personal Training", "Boxing", "Swimming"])
                with col2:
                    email = st.text_input("Email*")
                    phone = st.text_input("Phone*")
                    hire_date = st.date_input("Hire Date*", value=date.today())
                
                submitted = st.form_submit_button("Add Trainer")
                if submitted:
                    if first_name and last_name and email and phone and specialization:
                        success, message = insert_trainer(first_name, last_name, specialization, email, phone, hire_date)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all required fields!")
        
        # Insert Class
        with tab4:
            st.subheader("Add New Class")
            trainers_df = get_trainers()
            trainer_options = {f"{row['First_Name']} {row['Last_Name']} ({row['Specialization']})": row['Trainer_ID'] 
                             for _, row in trainers_df.iterrows()}
            
            with st.form("insert_class_form"):
                class_name = st.text_input("Class Name*")
                col1, col2 = st.columns(2)
                with col1:
                    class_type = st.selectbox("Class Type*", 
                                            ["Yoga", "CrossFit", "Pilates", "Spinning", "Zumba", "Boxing", "Swimming", "HIIT"])
                    trainer = st.selectbox("Trainer*", list(trainer_options.keys()))
                    schedule_day = st.selectbox("Schedule Day*", 
                                              ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                with col2:
                    schedule_time = st.time_input("Schedule Time*")
                    duration = st.number_input("Duration (Minutes)*", min_value=15, max_value=180, value=60, step=15)
                    capacity = st.number_input("Max Capacity*", min_value=1, max_value=100, value=20)
                
                submitted = st.form_submit_button("Add Class")
                if submitted:
                    if class_name and trainer:
                        trainer_id = trainer_options[trainer]
                        time_str = schedule_time.strftime("%H:%M")
                        success, message = insert_class(class_name, class_type, trainer_id, schedule_day, time_str, duration, capacity)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all required fields!")
        
        # Insert Booking
        with tab5:
            st.subheader("Add New Booking")
            members_df = get_members()
            classes_df = get_classes()
            
            member_options = {f"{row['First_Name']} {row['Last_Name']} (ID: {row['Member_ID']})": row['Member_ID'] 
                            for _, row in members_df.iterrows()}
            class_options = {f"{row['Class_Name']} - {row['Schedule_Day']} {row['Schedule_Time']}": row['Class_ID'] 
                           for _, row in classes_df.iterrows()}
            
            with st.form("insert_booking_form"):
                col1, col2 = st.columns(2)
                with col1:
                    member = st.selectbox("Member*", list(member_options.keys()))
                    class_sel = st.selectbox("Class*", list(class_options.keys()))
                with col2:
                    booking_date = st.date_input("Booking Date*", value=date.today())
                    status = st.selectbox("Attendance Status", ["Booked", "Attended", "Cancelled", "No-Show"])
                
                submitted = st.form_submit_button("Create Booking")
                if submitted:
                    if member and class_sel:
                        member_id = member_options[member]
                        class_id = class_options[class_sel]
                        success, message = insert_booking(member_id, class_id, booking_date, status)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all required fields!")
    
    # ========================================
    # DELETE DATA
    # ========================================
    elif menu == "❌ Delete Data":
        st.header("Delete Data")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Member", "🏋️ Trainer", "📅 Class", "🎫 Booking", "📋 Membership Plan"])
        
        # Delete Member
        with tab1:
            st.subheader("Delete Member")
            members_df = get_members()
            if not members_df.empty:
                st.dataframe(members_df, use_container_width=True)
                member_id = st.number_input("Enter Member ID to delete", min_value=1, step=1)
                if st.button("Delete Member", type="primary"):
                    success, message = delete_record("Members", "Member_ID", member_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No members in the database.")
        
        # Delete Trainer
        with tab2:
            st.subheader("Delete Trainer")
            trainers_df = get_trainers()
            if not trainers_df.empty:
                st.dataframe(trainers_df, use_container_width=True)
                trainer_id = st.number_input("Enter Trainer ID to delete", min_value=1, step=1)
                if st.button("Delete Trainer", type="primary"):
                    success, message = delete_record("Trainers", "Trainer_ID", trainer_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No trainers in the database.")
        
        # Delete Class
        with tab3:
            st.subheader("Delete Class")
            classes_df = get_classes()
            if not classes_df.empty:
                st.dataframe(classes_df, use_container_width=True)
                class_id = st.number_input("Enter Class ID to delete", min_value=1, step=1)
                if st.button("Delete Class", type="primary"):
                    success, message = delete_record("Classes", "Class_ID", class_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No classes in the database.")
        
        # Delete Booking
        with tab4:
            st.subheader("Delete Booking")
            bookings_df = get_bookings()
            if not bookings_df.empty:
                st.dataframe(bookings_df, use_container_width=True)
                booking_id = st.number_input("Enter Booking ID to delete", min_value=1, step=1)
                if st.button("Delete Booking", type="primary"):
                    success, message = delete_record("Class_Bookings", "Booking_ID", booking_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No bookings in the database.")
        
        # Delete Membership Plan
        with tab5:
            st.subheader("Delete Membership Plan")
            plans_df = get_membership_plans()
            if not plans_df.empty:
                st.dataframe(plans_df, use_container_width=True)
                plan_id = st.number_input("Enter Plan ID to delete", min_value=1, step=1)
                if st.button("Delete Plan", type="primary"):
                    success, message = delete_record("Membership_Plans", "Plan_ID", plan_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No membership plans in the database.")
    
    # ========================================
    # UPDATE DATA
    # ========================================
    elif menu == "✏️ Update Data":
        st.header("Update Data")
        
        tab1, tab2, tab3 = st.tabs(["👤 Update Member", "📅 Update Class", "🎫 Update Booking Status"])
        
        # Update Member
        with tab1:
            st.subheader("Update Member Information")
            members_df = get_members()
            
            if not members_df.empty:
                st.dataframe(members_df, use_container_width=True)
                
                with st.form("update_member_form"):
                    member_id = st.number_input("Member ID to Update*", min_value=1, step=1)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("New First Name*")
                        last_name = st.text_input("New Last Name*")
                        email = st.text_input("New Email*")
                    with col2:
                        phone = st.text_input("New Phone*")
                        status = st.selectbox("New Status", ["Active", "Inactive"])
                    
                    submitted = st.form_submit_button("Update Member")
                    if submitted:
                        if first_name and last_name and email and phone:
                            success, message = update_member(member_id, first_name, last_name, email, phone, status)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Please fill in all fields!")
            else:
                st.info("No members in the database.")
        
        # Update Class
        with tab2:
            st.subheader("Update Class Information")
            classes_df = get_classes()
            
            if not classes_df.empty:
                st.dataframe(classes_df, use_container_width=True)
                
                with st.form("update_class_form"):
                    class_id = st.number_input("Class ID to Update*", min_value=1, step=1)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        class_name = st.text_input("New Class Name*")
                        schedule_day = st.selectbox("New Schedule Day*", 
                                                   ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                    with col2:
                        schedule_time = st.time_input("New Schedule Time*")
                        max_capacity = st.number_input("New Max Capacity*", min_value=1, max_value=100, value=20)
                    
                    submitted = st.form_submit_button("Update Class")
                    if submitted:
                        if class_name:
                            time_str = schedule_time.strftime("%H:%M")
                            success, message = update_class(class_id, class_name, schedule_day, time_str, max_capacity)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Please fill in all fields!")
            else:
                st.info("No classes in the database.")
        
        # Update Booking Status
        with tab3:
            st.subheader("Update Booking Status")
            bookings_df = get_bookings()
            
            if not bookings_df.empty:
                st.dataframe(bookings_df, use_container_width=True)
                
                with st.form("update_booking_form"):
                    booking_id = st.number_input("Booking ID to Update*", min_value=1, step=1)
                    new_status = st.selectbox("New Attendance Status*", 
                                            ["Booked", "Attended", "Cancelled", "No-Show"])
                    
                    submitted = st.form_submit_button("Update Status")
                    if submitted:
                        success, message = update_booking_status(booking_id, new_status)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            else:
                st.info("No bookings in the database.")
    
    # ========================================
    # JOIN QUERIES
    # ========================================
    elif menu == "🔍 JOIN Queries":
        st.header("JOIN Query Results")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "👥 Members & Memberships", 
            "📅 Class Schedule", 
            "🎫 Member Bookings", 
            "📊 Trainer Workload"
        ])
        
        # Query 1: Members with Memberships
        with tab1:
            st.subheader("Members with Their Active Membership Plans")
            st.markdown("**JOIN: Members ⋈ Member_Memberships ⋈ Membership_Plans**")
            df = get_member_memberships_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Records: {len(df)}")
        
        # Query 2: Class Schedule
        with tab2:
            st.subheader("Complete Class Schedule with Trainer Information")
            st.markdown("**JOIN: Classes ⋈ Trainers**")
            df = get_class_schedule_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Classes: {len(df)}")
        
        # Query 3: Member Bookings
        with tab3:
            st.subheader("Member Class Bookings with Details")
            st.markdown("**JOIN: Class_Bookings ⋈ Members ⋈ Classes ⋈ Trainers**")
            df = get_member_bookings_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Bookings: {len(df)}")
        
        # Query 4: Trainer Workload
        with tab4:
            st.subheader("Trainer Workload Analysis")
            st.markdown("**JOIN: Trainers ⟕ Classes (LEFT JOIN with GROUP BY)**")
            df = get_trainer_workload_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Trainers: {len(df)}")
    
    # ========================================
    # VIEW TABLES
    # ========================================
    elif menu == "📊 View Tables":
        st.header("View All Tables")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "👤 Members", 
            "📋 Membership Plans", 
            "🔗 Member Memberships",
            "🏋️ Trainers", 
            "📅 Classes", 
            "🎫 Bookings"
        ])
        
        with tab1:
            st.subheader("Members Table")
            df = get_members()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Members: {len(df)}")
        
        with tab2:
            st.subheader("Membership Plans Table")
            df = get_membership_plans()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Plans: {len(df)}")
        
        with tab3:
            st.subheader("Member Memberships Table")
            df = get_all_records('Member_Memberships')
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Membership Records: {len(df)}")
        
        with tab4:
            st.subheader("Trainers Table")
            df = get_trainers()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Trainers: {len(df)}")
        
        with tab5:
            st.subheader("Classes Table")
            df = get_classes()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Classes: {len(df)}")
        
        with tab6:
            st.subheader("Class Bookings Table")
            df = get_bookings()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Bookings: {len(df)}")
    
    # Footer
    st.markdown("---")
    st.markdown("**CMPE 351 - Database Systems Project** | Fitness & Gym Membership Management System")

if __name__ == "__main__":
    main()
