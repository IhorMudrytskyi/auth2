import psycopg2
import streamlit as st

connection = psycopg2.connect(host = st.secrets['psql]['host'], 
                              user = st.secrets['psql]['user'],
                              password = st.secrets['psql]['password'],
                              database = st.secrets['psql]['database'],
                              port = st.secrets['psql']['port'])
                              
connection.autocommit = True
cursor = connection.cursor()

if 'active' not in st.session_state:
    st.session_state.active = 'main'

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Авторизація"):
        st.session_state.active = 'authorization'

with col2:
    if st.button("Реєстрація"):
        st.session_state.active= 'register'

with col3:
    if st.button("Зміна паролю"):
        st.session_state.active = 'change_password'

with col4:
    if st.button("Забули логін/пароль"):
        st.session_state.active = 'zab_login_pass'
    
if st.session_state.active == 'authorization':
    st.markdown(f"<h1 style = 'text-align: center>'Авторизація</h1>", unsafe_allow_html=True)
    auth_login = st.text_input("Логін", type='default',key='auth_login').replace(" ", "")
    auth_password = st.text_input("Пароль", type='password', key='auth_password').replace(" ", "")
    if st.button("Увійти"):
        cursor.execute("select * from auth where login = %s and password = %s;",(auth_login, auth_password))
        auth_result = cursor.fetchone()
        if auth_result:
            cursor.execute("select * from user_info join auth on user_info.id = auth.id where auth.login = %s and auth.password = %s;",(auth_login, auth_password))
            auth_result_2 = cursor.fetchone()
            st.success("Ви успішно ввішли!")
            st.markdown(f"<h3 style = 'text-align: center'>{auth_result_2[1]} {auth_result_2[2]}</h3>", unsafe_allow_html=True)
            st.text(f"Номер телефону: {auth_result_2[3]}")
            st.text(f"Електронна пошта: {auth_result_2[4]}")
        else:
            st.error("Неправильний логін/пароль!")

if st.session_state.active == 'register':
    st.markdown(f"<h1 style = 'text-align: center'>Реєстрація</h1>", unsafe_allow_html= True)
    reg_first_name = st.text_input("Ім'я", type='default',key='reg_first_name').replace(" ", "")
    reg_last_name = st.text_input("Прізвище", type='default', key='reg_last_name').replace(" ", "")
    reg_phone_number = st.text_input("Номер телефону", type='default',key='reg_phone_number').replace(" ", "")
    reg_email = st.text_input("Електронна пошта", type='default',key='reg_email').replace(" ", "")
    reg_login = st.text_input("Логін", type='default',key='reg_login').replace(" ", "")
    reg_password = st.text_input("Пароль", type='password',key='reg_password').replace(" ", "")
    if st.button("Створити акаунт"):
        cursor.execute("select * from auth where login = %s;",(reg_login,))
        login_result = cursor.fetchone()
        if login_result:
            st.error("Користувач з таким логіном вже існує!")
        else:
            cursor.execute("select * from user_info where email = %s;",(reg_email,))
            email_result = cursor.fetchone()
            if email_result:
                st.error("Користувач з такою електронною поштою вже існує!")
            else:
                cursor.execute("insert into auth(login, password) values (%s, %s) returning id;",(reg_login, reg_password))
                reg_id = cursor.fetchone()
                cursor.execute("insert into user_info(id, first_name, last_name, phone_number, email) values (%s, %s, %s, %s, %s);",(reg_id, reg_first_name, reg_last_name, reg_phone_number, reg_email))
                st.succes("Акаунт успішно створено!")
            
if st.session_state.active == 'change_password':
    st.markdown(f"<h1 style = 'text-align: center'>Зміна паролю</h1>", unsafe_allow_html= True)
    change_login = st.text_input("Логін", type='default', key='change_login').replace(" ", "")
    old_password = st.text_input("Старий пароль", type='password', key='old_password').replace(" ", "")
    new_password_1 = st.text_input("Новий пароль", type='password', key='new_password_1').replace(" ", "")
    new_password_2 = st.text_input("Повторіть новий пароль", type='password', key='new_password_2').replace(" ", "")
    if st.button("Змінити пароль"):
        cursor.execute("select * from auth where login = %s;",(change_login,))
        change_password_login_result  = cursor.fetchone()
        if change_password_login_result:
            if new_password_1 == new_password_2:
                cursor.execute("update auth set password = %s where login = %s;",(new_password_1,change_login))
                st.success("Пароль успішно змінено!")
            else:
                st.error("Паролі не збігаються!")
        else:
            st.error("Користувача з таким логіном не знайдено!")

if st.session_state.active == 'zab_login_pass':
    
    if 'zab_login' not in st.session_state:
        st.session_state.zab_login = False
  
    if 'zab_password' not in st.session_state:
        st.session_state.zab_password = False

    col5, col6 = st.columns(2)

    with col5:
        if st.button("Забули логін"):
            st.session_state.zab_password = False
            st.session_state.zab_login = True

    with col6:
        if st.button("Забули пароль"):
            st.session_state.zab_login = False
            st.session_state.zab_password = True

    if st.session_state.zab_login:
        zab_login_first_name = st.text_input("Ім'я", type='default', key='zab_login_first_name').replace(' ', '')
        zab_login_last_name = st.text_input("Прізвище", type='default', key='zab_login_last_name').replace(' ', '')
        zab_login_phone_number = st.text_input("Номер телефону", type='default', key='zab_login_phone_number').replace(' ', '')
        zab_login_email = st.text_input("Електронна пошта", type='default', key='zab_login_email').replace(' ', '')
        if st.button("Нагадати логін"):
            cursor.execute("""select auth.login from auth 
                        join user_info in auth.id = user_info.id
                        where user_info.first_name = %s
                        and user_info.last_name = %s
                        and user_info.phone_number = %s
                        and user_info.email = %s;"""
                        ,(zab_login_first_name, zab_login_last_name, zab_login_phone_number, zab_login_email))
            zab_login_result = cursor.fetchone()
            if zab_login_result:
                st.succes(f"Ваш логін для входу: {zab_login_result[0]}")
            else:
                st.error("Користувача з такими даними не знайдено!")

    if st.session_state.zab_password:
        zab_pass_login = st.text_input("Логін", type= 'default', key='zab_pass_login').replace(' ', '')
        zab_pass_phone_number = st.text_input("Номер телефону", type='default', key='zab_pass_phone_number').replace(' ', '')
        zab_pass_email = st.text_input("Електронна пошта", type='default', key='zab_pass_email').replace(' ', '')
        zab_pass_old_password = st.text_input("Старий пароль", type='password', key = 'zab_pass_old_password').replace(' ', '')
        zab_pass_new_password_1 = st.text_input("Новий пароль", type='password', key = 'zab_pass_new_password_1').replace(' ', '')
        zab_pass_new_password_2 = st.text_input("Повторіть новий пароль", type='password', key = 'zab_pass_new_password_2').replace(' ', '')
        if st.button("Змінити пароль"):
            cursor.execute("""select * from user_info
                        join auth on user_info.id = auth.id
                        where user_info.phone_number = %s
                        and user_info.email = %s
                        and auth.login = %s
                        and auth.password = %s;"""
                        ,(zab_pass_phone_number, zab_pass_email, zab_pass_login, zab_pass_old_password))
            zab_pass_result = cursor.fetchone()
            if zab_pass_result:
                if zab_pass_new_password_1 == zab_pass_new_password_2:
                    cursor.execute("update auth set password = %s where login = %s;",(zab_pass_new_password_2, zab_pass_login))
                    st.success("Пароль успішно змінено!")
                else:
                    st.error("Паролі не збігаються!")
            else:
                st.error("Користувача з такими даними не знайдено!")


cursor.close()
connection.close()
