"""
Fitness & Gym Membership Management System
CMPE 351 - Database Systems Project
Nehir Gürsoy 122200051
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import os

# DATABASE SETUP & CONNECTION

def get_connection():
    conn = sqlite3.connect('gym_management.db', check_same_thread=False)
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table 1: MEMBERS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Members (
        Member_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        First_Name TEXT NOT NULL,
        Last_Name TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Phone TEXT UNIQUE NOT NULL,
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
        Phone TEXT UNIQUE NOT NULL,
        Hire_Date DATE NOT NULL
    )
    ''')
    
    # Table 5: CLASSES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Classes (
        Class_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Class_Name TEXT UNIQUE NOT NULL,
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
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Members")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  
    
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

# VALIDATION FUNCTIONS

def check_member_has_membership(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM Member_Memberships 
        WHERE Member_ID = ?
    ''', (member_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def check_member_has_active_membership(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM Member_Memberships 
        WHERE Member_ID = ? AND Is_Active = 1
    ''', (member_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# CRUD OPERATIONS

def insert_member(first_name, last_name, email, phone, dob, join_date, status):
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

# JOIN QUERIES

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

# UTILITY FUNCTIONS

def get_all_records(table_name):
    """Get all records from a table"""
    conn = get_connection()
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
    conn.close()
    return df

def get_members():
    return get_all_records('Members')

def get_trainers():
    return get_all_records('Trainers')

def get_classes():
    return get_all_records('Classes')

def get_bookings():
    return get_all_records('Class_Bookings')

def get_membership_plans():
    return get_all_records('Membership_Plans')

# STREAMLIT UI

def main():
    st.set_page_config(
        page_title="Gym Management System",
        page_icon="💪",
        layout="wide"
    )
    
    create_tables()
    insert_sample_data()

    st.title("💪 Fitness & Gym Membership Management System")
    st.markdown("**CMPE 351 - Database Systems Project | Nehir Gürsoy 122200051**")
    st.markdown("---")
    
    st.sidebar.title("MENU")
    menu = st.sidebar.radio(
        "Select Operation:",
        ["🏠 Home", "➕ Insert", "❌ Delete", "✏️ Update", "🔍 JOIN", "📊 View Tables"]
    )
    
    # HOME PAGE
    if menu == "🏠 Home":
        st.header("Welcome to Gym Management System!")
        
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
    
    # INSERT DATA
    elif menu == "➕ Insert":
        st.header("Insert New Data")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Member", "📋 Membership Plan", "🏋️ Trainer", "📅 Class", "🎫 Booking"])
        
        with tab1:
            st.subheader("Add New Member")
            st.info("⚠️ Every member must have a membership plan. Please select a plan below.")
            
            plans_df = get_membership_plans()
            plan_options = {f"{row['Plan_Name']} - ${row['Price']} ({row['Duration_Months']} months)": row['Plan_ID'] 
                          for _, row in plans_df.iterrows()}
            
            with st.form("insert_member_form"):
                st.markdown("**Member Information**")
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
                
                st.markdown("---")
                st.markdown("**Initial Membership Plan** (Required)")
                selected_plan = st.selectbox("Select Membership Plan*", list(plan_options.keys()))
                
                col3, col4 = st.columns(2)
                with col3:
                    start_date = st.date_input("Membership Start Date*", value=date.today())
                with col4:
                    payment_status = st.selectbox("Payment Status*", ["Paid", "Pending"])
                
                submitted = st.form_submit_button("Add Member with Membership")
                if submitted:
                    if first_name and last_name and email and phone and selected_plan:
                        success, message = insert_member(first_name, last_name, email, phone, dob, join_date, status)
                        if success:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT Member_ID FROM Members WHERE Email = ?", (email,))
                            member_id = cursor.fetchone()[0]
                            
                            plan_id = plan_options[selected_plan]
                            cursor.execute("SELECT Duration_Months FROM Membership_Plans WHERE Plan_ID = ?", (plan_id,))
                            duration = cursor.fetchone()[0]
                            
                            end_date = start_date + timedelta(days=duration * 30)
                            
                            cursor.execute('''
                                INSERT INTO Member_Memberships (Member_ID, Plan_ID, Start_Date, End_Date, Payment_Status, Is_Active)
                                VALUES (?, ?, ?, ?, ?, 1)
                            ''', (member_id, plan_id, start_date, end_date, payment_status))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Member added successfully with {selected_plan}!")
                            st.balloons()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all required fields!")
        
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
    
    # DELETE DATA
    elif menu == "❌ Delete":
        st.header("Delete Data")
        st.info("💡 You can delete entire records OR specific fields (set to NULL/default)")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Member", "🏋️ Trainer", "📅 Class", "🎫 Booking", "📋 Plan"])
        
        with tab1:
            st.subheader("Delete Member Data")
            members_df = get_members()
            
            if not members_df.empty:
                st.dataframe(members_df, use_container_width=True)
                
                delete_type = st.radio("What to delete?", ["Entire Member Record", "Specific Field Data"], horizontal=True)
                
                if delete_type == "Entire Member Record":
                    st.warning("⚠️ This will delete the member and all their memberships and bookings (CASCADE)")
                    member_id = st.number_input("Member ID to delete", min_value=1, step=1)
                    if st.button("🗑️ Delete Entire Member", type="primary"):
                        success, msg = delete_record("Members", "Member_ID", member_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("Clear specific field (phone can be cleared, but email cannot as it's required)")
                    member_id = st.number_input("Member ID", min_value=1, step=1)
                    field = st.selectbox("Field to clear", ["Phone"])
                    st.caption("Note: Phone will be set to empty. Other fields cannot be cleared as they're required.")
                    
                    if st.button("Clear Field"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            # For phone, we need a default value since it's UNIQUE NOT NULL
                            cursor.execute(f"UPDATE Members SET {field} = ? WHERE Member_ID = ?", 
                                         (f'CLEARED-{member_id}', member_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ {field} cleared!")
                                st.rerun()
                            else:
                                st.error("Member not found!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        finally:
                            conn.close()
            else:
                st.info("No members in database.")
        
        with tab2:
            st.subheader("Delete Trainer Data")
            trainers_df = get_trainers()
            
            if not trainers_df.empty:
                st.dataframe(trainers_df, use_container_width=True)
                
                delete_type = st.radio("What to delete?", ["Entire Trainer Record", "Specific Field Data"], horizontal=True, key="del_trainer")
                
                if delete_type == "Entire Trainer Record":
                    st.warning("⚠️ Cannot delete if trainer has members or classes assigned (RESTRICT)")
                    trainer_id = st.number_input("Trainer ID to delete", min_value=1, step=1)
                    if st.button("🗑️ Delete Entire Trainer", type="primary"):
                        success, msg = delete_record("Trainers", "Trainer_ID", trainer_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("Clear specific field data")
                    trainer_id = st.number_input("Trainer ID", min_value=1, step=1, key="tr_id_field")
                    field = st.selectbox("Field to clear", ["Phone"])
                    st.caption("Note: Only non-critical fields can be cleared")
                    
                    if st.button("Clear Field", key="clear_trainer"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f"UPDATE Trainers SET {field} = ? WHERE Trainer_ID = ?", 
                                         (f'CLEARED-{trainer_id}', trainer_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ {field} cleared!")
                                st.rerun()
                            else:
                                st.error("Trainer not found!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        finally:
                            conn.close()
            else:
                st.info("No trainers in database.")
        
        with tab3:
            st.subheader("Delete Class Data")
            classes_df = get_classes()
            
            if not classes_df.empty:
                st.dataframe(classes_df, use_container_width=True)
                
                delete_type = st.radio("What to delete?", ["Entire Class Record", "Specific Field Data"], horizontal=True, key="del_class")
                
                if delete_type == "Entire Class Record":
                    st.warning("⚠️ This will also delete all bookings for this class (CASCADE)")
                    class_id = st.number_input("Class ID to delete", min_value=1, step=1)
                    if st.button("🗑️ Delete Entire Class", type="primary"):
                        success, msg = delete_record("Classes", "Class_ID", class_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("Clear specific field data (capacity can be reduced)")
                    class_id = st.number_input("Class ID", min_value=1, step=1, key="cl_id_field")
                    field = st.selectbox("Field to modify", ["Max_Capacity"])
                    
                    if field == "Max_Capacity":
                        new_value = st.number_input("New Capacity (0 to close class)", min_value=0, value=0)
                        if st.button("Update Capacity", key="update_class_cap"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            try:
                                cursor.execute(f"UPDATE Classes SET {field} = ? WHERE Class_ID = ?", 
                                             (new_value, class_id))
                                conn.commit()
                                if cursor.rowcount > 0:
                                    st.success(f"✅ Capacity updated to {new_value}!")
                                    st.rerun()
                                else:
                                    st.error("Class not found!")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                            finally:
                                conn.close()
            else:
                st.info("No classes in database.")
        
        with tab4:
            st.subheader("Delete Booking Data")
            bookings_df = get_bookings()
            
            if not bookings_df.empty:
                st.dataframe(bookings_df, use_container_width=True)
                
                delete_type = st.radio("What to delete?", ["Entire Booking Record", "Cancel Booking"], horizontal=True, key="del_booking")
                
                if delete_type == "Entire Booking Record":
                    st.warning("⚠️ Permanently remove booking from system")
                    booking_id = st.number_input("Booking ID to delete", min_value=1, step=1)
                    if st.button("🗑️ Delete Entire Booking", type="primary"):
                        success, msg = delete_record("Class_Bookings", "Booking_ID", booking_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("Change booking status to 'Cancelled' instead of deleting")
                    booking_id = st.number_input("Booking ID", min_value=1, step=1, key="bk_id_field")
                    
                    if st.button("Cancel Booking", key="cancel_booking"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute("UPDATE Class_Bookings SET Attendance_Status = 'Cancelled' WHERE Booking_ID = ?", 
                                         (booking_id,))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success("✅ Booking cancelled!")
                                st.rerun()
                            else:
                                st.error("Booking not found!")
                        finally:
                            conn.close()
            else:
                st.info("No bookings in database.")
        
        with tab5:
            st.subheader("Delete Membership Plan Data")
            plans_df = get_membership_plans()
            
            if not plans_df.empty:
                st.dataframe(plans_df, use_container_width=True)
                
                delete_type = st.radio("What to delete?", ["Entire Plan Record", "Specific Field Data"], horizontal=True, key="del_plan")
                
                if delete_type == "Entire Plan Record":
                    st.warning("⚠️ Cannot delete if plan is assigned to members (RESTRICT)")
                    plan_id = st.number_input("Plan ID to delete", min_value=1, step=1)
                    if st.button("🗑️ Delete Entire Plan", type="primary"):
                        success, msg = delete_record("Membership_Plans", "Plan_ID", plan_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("Modify plan details")
                    plan_id = st.number_input("Plan ID", min_value=1, step=1, key="pl_id_field")
                    field = st.selectbox("Field to modify", ["Price", "Benefits_Description"])
                    
                    if field == "Price":
                        new_value = st.number_input("New Price ($)", min_value=0.0, value=0.0, step=10.0)
                    else:
                        new_value = st.text_area("New Benefits", value="Plan discontinued")
                    
                    if st.button("Update Field", key="update_plan_field"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f"UPDATE Membership_Plans SET {field} = ? WHERE Plan_ID = ?", 
                                         (new_value, plan_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ {field} updated!")
                                st.rerun()
                            else:
                                st.error("Plan not found!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        finally:
                            conn.close()
            else:
                st.info("No plans in database.")
    
    # UPDATE DATA (IMPROVED)
    elif menu == "✏️ Update":
        st.header("Update Data")
        st.info("💡 Step 1: Select by ID/Name → Step 2: Choose Field → Step 3: Enter New Value")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Member", "🏋️ Trainer", "📋 Plan", "📅 Class", "🎫 Booking"])
        
        # Update Member
        with tab1:
            st.subheader("Update Member")
            members_df = get_members()
            
            if not members_df.empty:
                st.dataframe(members_df, use_container_width=True)
                
                with st.form("update_member_form"):
                    st.markdown("**Step 1: Select Member**")
                    member_id = st.number_input("Member ID*", min_value=1, step=1)
                    
                    st.markdown("**Step 2: Choose Field to Update**")
                    field = st.selectbox("Field*", ['First_Name', 'Last_Name', 'Email', 'Phone', 'Status'])
                    
                    st.markdown("**Step 3: Enter New Value**")
                    if field == 'Status':
                        new_value = st.selectbox("New Value*", ['Active', 'Inactive'])
                    else:
                        new_value = st.text_input("New Value*")
                    
                    submitted = st.form_submit_button("✅ Update Member", type="primary")
                    if submitted and new_value:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f'UPDATE Members SET {field} = ? WHERE Member_ID = ?', (new_value, member_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Member {field} updated!")
                                st.rerun()
                            else:
                                st.error("Member not found!")
                        except sqlite3.IntegrityError:
                            st.error("Error: This value already exists (must be unique)!")
                        finally:
                            conn.close()
            else:
                st.info("No members in database.")
        
        # Update Trainer
        with tab2:
            st.subheader("Update Trainer")
            trainers_df = get_trainers()
            
            if not trainers_df.empty:
                st.dataframe(trainers_df, use_container_width=True)
                
                with st.form("update_trainer_form"):
                    st.markdown("**Step 1: Select Trainer**")
                    trainer_id = st.number_input("Trainer ID*", min_value=1, step=1)
                    
                    st.markdown("**Step 2: Choose Field to Update**")
                    field = st.selectbox("Field*", ['First_Name', 'Last_Name', 'Specialization', 'Email', 'Phone'])
                    
                    st.markdown("**Step 3: Enter New Value**")
                    if field == 'Specialization':
                        new_value = st.selectbox("New Value*", ["Yoga", "CrossFit", "Pilates", "Spinning", "Zumba", "Personal Training", "Boxing", "Swimming"])
                    else:
                        new_value = st.text_input("New Value*")
                    
                    submitted = st.form_submit_button("✅ Update Trainer", type="primary")
                    if submitted and new_value:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f'UPDATE Trainers SET {field} = ? WHERE Trainer_ID = ?', (new_value, trainer_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Trainer {field} updated!")
                                st.rerun()
                            else:
                                st.error("Trainer not found!")
                        except sqlite3.IntegrityError:
                            st.error("Error: This value already exists (must be unique)!")
                        finally:
                            conn.close()
            else:
                st.info("No trainers in database.")
        
        # Update Plan
        with tab3:
            st.subheader("Update Membership Plan")
            plans_df = get_membership_plans()
            
            if not plans_df.empty:
                st.dataframe(plans_df, use_container_width=True)
                
                with st.form("update_plan_form"):
                    st.markdown("**Step 1: Select Plan**")
                    selection_method = st.radio("Select by:", ["Plan ID", "Plan Name"], horizontal=True, key="plan_select")
                    
                    if selection_method == "Plan ID":
                        plan_id = st.number_input("Plan ID*", min_value=1, step=1)
                    else:
                        name_list = plans_df['Plan_Name'].tolist()
                        selected_name = st.selectbox("Select Plan Name*", name_list)
                        plan_id = plans_df[plans_df['Plan_Name'] == selected_name]['Plan_ID'].values[0]
                    
                    st.markdown("**Step 2: Choose Field to Update**")
                    field = st.selectbox("Field*", ['Plan_Name', 'Duration_Months', 'Price', 'Benefits_Description'])
                    
                    st.markdown("**Step 3: Enter New Value**")
                    if field == 'Duration_Months':
                        new_value = st.number_input("New Value (months)*", min_value=1, max_value=24, value=1)
                    elif field == 'Price':
                        new_value = st.number_input("New Value ($)*", min_value=0.0, value=50.0, step=10.0)
                    else:
                        new_value = st.text_input("New Value*")
                    
                    submitted = st.form_submit_button("✅ Update Plan", type="primary")
                    if submitted and new_value:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f'UPDATE Membership_Plans SET {field} = ? WHERE Plan_ID = ?', (new_value, plan_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Plan {field} updated!")
                                st.rerun()
                            else:
                                st.error("Plan not found!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        finally:
                            conn.close()
            else:
                st.info("No plans in database.")
        
        # Update Class
        with tab4:
            st.subheader("Update Class")
            classes_df = get_classes()
            
            if not classes_df.empty:
                st.dataframe(classes_df, use_container_width=True)
                
                with st.form("update_class_form"):
                    st.markdown("**Step 1: Select Class**")
                    selection_method = st.radio("Select by:", ["Class ID", "Class Name"], horizontal=True, key="class_select")
                    
                    if selection_method == "Class ID":
                        class_id = st.number_input("Class ID*", min_value=1, step=1)
                    else:
                        name_list = classes_df['Class_Name'].tolist()
                        selected_name = st.selectbox("Select Class Name*", name_list)
                        class_id = classes_df[classes_df['Class_Name'] == selected_name]['Class_ID'].values[0]
                    
                    st.markdown("**Step 2: Choose Field to Update**")
                    field = st.selectbox("Field*", ['Class_Name', 'Schedule_Day', 'Schedule_Time', 'Duration_Minutes', 'Max_Capacity'])
                    
                    st.markdown("**Step 3: Enter New Value**")
                    if field == 'Schedule_Day':
                        new_value = st.selectbox("New Value*", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                    elif field == 'Schedule_Time':
                        time_val = st.time_input("New Value*")
                        new_value = time_val.strftime("%H:%M")
                    elif field in ['Duration_Minutes', 'Max_Capacity']:
                        new_value = st.number_input("New Value*", min_value=1, value=30)
                    else:
                        new_value = st.text_input("New Value*")
                    
                    submitted = st.form_submit_button("✅ Update Class", type="primary")
                    if submitted and new_value:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f'UPDATE Classes SET {field} = ? WHERE Class_ID = ?', (new_value, class_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Class {field} updated!")
                                st.rerun()
                            else:
                                st.error("Class not found!")
                        except sqlite3.IntegrityError:
                            st.error("Error: Class name must be unique!")
                        finally:
                            conn.close()
            else:
                st.info("No classes in database.")
        
        # Update Booking
        with tab5:
            st.subheader("Update Booking")
            bookings_df = get_bookings()
            
            if not bookings_df.empty:
                st.dataframe(bookings_df, use_container_width=True)
                
                with st.form("update_booking_form"):
                    st.markdown("**Step 1: Select Booking**")
                    booking_id = st.number_input("Booking ID*", min_value=1, step=1)
                    
                    st.markdown("**Step 2: Choose Field to Update**")
                    field = st.selectbox("Field*", ['Attendance_Status'])
                    
                    st.markdown("**Step 3: Enter New Value**")
                    new_value = st.selectbox("New Status*", ["Booked", "Attended", "Cancelled", "No-Show"])
                    
                    submitted = st.form_submit_button("✅ Update Booking", type="primary")
                    if submitted:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f'UPDATE Class_Bookings SET {field} = ? WHERE Booking_ID = ?', (new_value, booking_id))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Booking updated!")
                                st.rerun()
                            else:
                                st.error("Booking not found!")
                        finally:
                            conn.close()
            else:
                st.info("No bookings in database.")
    
    # JOIN QUERIES
    elif menu == "🔍 JOIN":
        st.header("JOIN Query Results")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👥 Members & Memberships", 
            "📅 Class Schedule", 
            "🎫 Member Bookings", 
            "📊 Trainer Workload",
            "🔧 Custom JOIN"
        ])
        
        with tab1:
            st.subheader("Members with Their Active Membership Plans")
            st.markdown("**JOIN: Members ⋈ Member_Memberships ⋈ Membership_Plans**")
            df = get_member_memberships_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Records: {len(df)}")
        
        with tab2:
            st.subheader("Complete Class Schedule with Trainer Information")
            st.markdown("**JOIN: Classes ⋈ Trainers**")
            df = get_class_schedule_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Classes: {len(df)}")
        
        with tab3:
            st.subheader("Member Class Bookings with Details")
            st.markdown("**JOIN: Class_Bookings ⋈ Members ⋈ Classes ⋈ Trainers**")
            df = get_member_bookings_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Bookings: {len(df)}")
        
        with tab4:
            st.subheader("Trainer Workload Analysis")
            st.markdown("**JOIN: Trainers ⟕ Classes (LEFT JOIN with GROUP BY)**")
            df = get_trainer_workload_join()
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Trainers: {len(df)}")
        
        with tab5:
            st.subheader("🔧 Custom JOIN Builder")
            st.info("💡 Select tables you want to join and we'll show the combined data")
            
            # Available tables and their relationships
            available_tables = {
                "Members": "Members",
                "Membership Plans": "Membership_Plans",
                "Member Memberships": "Member_Memberships",
                "Trainers": "Trainers",
                "Classes": "Classes",
                "Class Bookings": "Class_Bookings"
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Select Tables to JOIN:**")
                selected_tables = st.multiselect(
                    "Choose 2 or more tables",
                    list(available_tables.keys()),
                    default=["Members", "Member Memberships"]
                )
            
            with col2:
                if len(selected_tables) >= 2:
                    st.markdown("**JOIN Type:**")
                    join_type = st.radio("Type", ["INNER JOIN", "LEFT JOIN"], horizontal=True)
                else:
                    st.warning("⚠️ Select at least 2 tables to join")
            
            if st.button("🔍 Execute JOIN Query", type="primary") and len(selected_tables) >= 2:
                try:
                    conn = get_connection()
                    
                    # Build query based on selected tables
                    table_names = [available_tables[t] for t in selected_tables]
                    
                    # Smart JOIN logic based on common patterns
                    if "Members" in table_names and "Member_Memberships" in table_names:
                        if "Membership_Plans" in table_names:
                            # Members + Memberships + Plans
                            query = f'''
                            SELECT m.*, mm.Start_Date, mm.End_Date, mm.Payment_Status, 
                                   mp.Plan_Name, mp.Price
                            FROM Members m
                            {join_type} Member_Memberships mm ON m.Member_ID = mm.Member_ID
                            {join_type} Membership_Plans mp ON mm.Plan_ID = mp.Plan_ID
                            '''
                        else:
                            # Members + Memberships
                            query = f'''
                            SELECT m.*, mm.Start_Date, mm.End_Date, mm.Payment_Status, mm.Is_Active
                            FROM Members m
                            {join_type} Member_Memberships mm ON m.Member_ID = mm.Member_ID
                            '''
                    
                    elif "Classes" in table_names and "Trainers" in table_names:
                        if "Class_Bookings" in table_names:
                            # Classes + Trainers + Bookings
                            query = f'''
                            SELECT c.Class_Name, c.Schedule_Day, c.Schedule_Time,
                                   t.First_Name || ' ' || t.Last_Name AS Trainer,
                                   cb.Booking_Date, cb.Attendance_Status
                            FROM Classes c
                            {join_type} Trainers t ON c.Trainer_ID = t.Trainer_ID
                            {join_type} Class_Bookings cb ON c.Class_ID = cb.Class_ID
                            '''
                        else:
                            # Classes + Trainers
                            query = f'''
                            SELECT c.*, t.First_Name || ' ' || t.Last_Name AS Trainer_Name,
                                   t.Specialization
                            FROM Classes c
                            {join_type} Trainers t ON c.Trainer_ID = t.Trainer_ID
                            '''
                    
                    elif "Members" in table_names and "Class_Bookings" in table_names:
                        if "Classes" in table_names:
                            # Members + Bookings + Classes
                            query = f'''
                            SELECT m.First_Name || ' ' || m.Last_Name AS Member,
                                   c.Class_Name, c.Schedule_Day, c.Schedule_Time,
                                   cb.Booking_Date, cb.Attendance_Status
                            FROM Members m
                            {join_type} Class_Bookings cb ON m.Member_ID = cb.Member_ID
                            {join_type} Classes c ON cb.Class_ID = c.Class_ID
                            '''
                        else:
                            # Members + Bookings
                            query = f'''
                            SELECT m.*, cb.Booking_Date, cb.Attendance_Status
                            FROM Members m
                            {join_type} Class_Bookings cb ON m.Member_ID = cb.Member_ID
                            '''
                    
                    elif "Trainers" in table_names and "Classes" in table_names:
                        # Trainers + Classes
                        query = f'''
                        SELECT t.First_Name || ' ' || t.Last_Name AS Trainer,
                               t.Specialization,
                               c.Class_Name, c.Schedule_Day, c.Schedule_Time
                        FROM Trainers t
                        {join_type} Classes c ON t.Trainer_ID = c.Trainer_ID
                        '''
                    
                    else:
                        # Generic JOIN for other combinations
                        query = f"SELECT * FROM {table_names[0]}"
                        st.info("⚠️ This combination requires manual JOIN conditions. Showing first table only.")
                    
                    st.markdown(f"**Executing Query:**")
                    st.code(query, language="sql")
                    
                    df = pd.read_sql_query(query, conn)
                    conn.close()
                    
                    st.success(f"✅ JOIN executed successfully! Found {len(df)} records")
                    st.dataframe(df, use_container_width=True)
                    
                    # Show query info
                    st.markdown("**Query Information:**")
                    st.write(f"- Tables joined: {', '.join(selected_tables)}")
                    st.write(f"- JOIN type: {join_type}")
                    st.write(f"- Total rows: {len(df)}")
                    st.write(f"- Total columns: {len(df.columns)}")
                    
                except Exception as e:
                    st.error(f"Error executing JOIN: {str(e)}")
                    st.info("💡 Tip: Make sure selected tables have relationship columns (foreign keys)")
            
            # Show helpful information
            st.markdown("---")
            st.markdown("**💡 Common JOIN Patterns:**")
            st.write("• **Members + Member Memberships + Plans**: See members with their subscription details")
            st.write("• **Classes + Trainers**: See which trainer teaches which class")
            st.write("• **Members + Class Bookings + Classes**: See member booking history")
            st.write("• **Trainers + Classes + Bookings**: See trainer schedule with bookings")
    
    # VIEW TABLES
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
    
    st.markdown("---")
    st.markdown("**CMPE 351 - Database Systems Project** | Nehir Gürsoy 122200051")

if __name__ == "__main__":
    main()