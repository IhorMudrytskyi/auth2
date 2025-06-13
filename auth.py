import psycopg2
import streamlit as st

connection = psycopg2.connect(
    host = st.secrets['psql']['host'],
    port = st.secrets['psql']['port'],
    database = st.secrets['psql']['database'],
    user = st.secrets['psql']['user'],
    password = st.secrets['psql']['password'])                              
cursor = connection.cursor()
connection.autocommit = True

col1, col2, col3, col4 = st.columns(4)

if "active" not in st.session_state:
    st.session_state.active = 'main'

with col1:
    if st.button("Авторизація"):
        st.session_state.active = 'authorization'

with col2:
    if st.button("Реєстрація"):
        st.session_state.active = 'register'

with col3:
    if st.button("Змінити пароль"):
        st.session_state.active = 'change_password'

with col4:
    if st.button("Забув логін/пароль"):
        st.session_state.active = 'zab'

if st.session_state.active == 'authorization':
    st.markdown(f"<h1 style = 'text-align: center'> Авторизація </h1>", unsafe_allow_html=True)
    auth_login = st.text_input("Логін", type='default',key='auth_login').replace(' ', '')
    auth_password = st.text_input("Пароль", type='password',key='auth_password').replace(' ', '')
    if st.button("Увійти"):
        cursor.execute("select * from auth where login = %s and password = %s;",(auth_login, auth_password))
        auth_result = cursor.fetchone()
        if auth_result:
            cursor.execute("""select * from user_info
                           join auth on user_info.id = auth.id
                           where auth.login = %s
                           and auth.password = %s;""",(auth_login, auth_password))
            info_result = cursor.fetchone()
            st.success("Ви успішно ввішли!")
            st.header("Ваші дані: ")
            st.markdown(f"<h3 style='text-align: center;'>{info_result[1]} {info_result[2]}</h3>", unsafe_allow_html=True)
            st.text(f"Номер телефону: {info_result[3]}")
            st.text(f"Електронна пошта: {info_result[4]}")
        else:
            st.error("Користувача з таким логіном/паролем не знайдено!")

if st.session_state.active == 'register':
    st.markdown(f"<h1 style = 'text-align: center'> Реєстрація </h1>", unsafe_allow_html=True)
    reg_first_name = st.text_input("Ім'я", type='default',key='reg_first_name').replace(' ', '')
    reg_last_name = st.text_input("Прізвище", type='default',key='reg_last_name').replace(' ', '')
    reg_phone_number = st.text_input("Номер телефону", type='default',key='reg_phone_number').replace(' ', '')
    reg_email = st.text_input("Електронна пошта", type='default',key='reg_email').replace(' ', '')
    reg_login = st.text_input("Логін", type='default',key='reg_login').replace(' ', '')
    reg_password = st.text_input("Пароль", type='password',key='reg_password').replace(' ', '')
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
                cursor.execute("insert into user_info(id, first_name, last_name, phone_number, email) values (%s, %s, %s, %s, %s);"
                               ,(reg_id, reg_first_name, reg_last_name, reg_phone_number, reg_email))
                st.success("Акаунт успішно створено!")

if st.session_state.active == 'change_password':
    st.markdown(f"<h1 style = 'text-align: center'> Зміна паролю </h1>", unsafe_allow_html=True)
    change_login = st.text_input("Логін", type='default', key='change_login').replace(" ", "")
    change_password = st.text_input("Старий пароль", type='password', key='change_password').replace(" ", "")
    change_password_1 = st.text_input("Новий пароль", type='password', key='change_password_1').replace(" ", "")
    change_password_2 = st.text_input("Повторіть новий пароль", type='password', key='change_password_2').replace(" ", "")
    if st.button("Змінити пароль "):
        cursor.execute("select * from auth where login = %s and password = %s;",(change_login, change_password))
        change_result = cursor.fetchone()
        if change_result:
            if change_password_1 == change_password_2:
                cursor.execute("update auth set password = %s where login = %s;",(change_password_1, change_login))
                st.success("Пароль успішно змінено!")
            else:
                st.error("Паролі не збігаються!")
        else:
            st.error("Невірно введений логін/пароль!")

if st.session_state.active == 'zab':
    col5, col6 = st.columns(2)

    with col5:
        if st.button("Забули логін"):
            st.session_state.active = 'zab_login'

    with col6:
        if st.button("Забули пароль"):
            st.session_state.active = 'zab_password'

    if st.session_state.active == 'zab_login':
        if 'zab_login2' not in st.session_state:
            st.session_state.zab_login2 = False
        
        if st.session_state.zab_login2:
            st.markdown(f"<h2 style = 'text-align: center'>Забув логін</h2>", unsafe_allow_html=True)
            zab_login_first_name = st.text_input("Ім'я", type='default',key='zab_login_first_name').replace(" ", "")
            zab_login_last_name = st.text_input("Прізвище", type='default',key='zab_login_last_name').replace(" ", "")
            zab_login_phone_number = st.text_input("Номер телефону", type='default',key='zab_login_phone_number').replace(" ", "")
            zab_login_email = st.text_input("Електронна пошта", type='default',key='zab_login_email').replace(" ", "")
            if st.button("Нагадати логін"):
                cursor.execute("""select login from auth
                                    join user_info ui on auth.id = ui.id
                                    where ui.first_name = %s
                                    and ui.last_name = %s
                                    and ui.phone_number = %s
                                    and ui.email = %s;""",(zab_login_first_name, zab_login_last_name, zab_login_phone_number, zab_login_email))
                zab_login_result = cursor.fetchone()
                if zab_login_result:
                    st.success(f"Логін для входу: {zab_login_result[0]}")
                else:
                    st.error("Користувача з такими даними не знайдено!")

    if st.session_state.active == 'zab_password':
        if 'zab_password2' not in st.session_state:
            st.session_state.zab_password2 = False   

        if st.session_state.zab_password2:
            st.markdown(f"<h2 style = 'text-align: center'>Забули пароль</h2>", unsafe_allow_html=True)
            zab_password_login = st.text_input("Логін", type='default',key='zab_password_login').replace(' ', '')
            zab_password_phone_number = st.text_input("Номер телефону", type='default',key='zab_password_phone_number').replace(' ', '')
            zab_password_email = st.text_input("Електронна пошта", type='default',key='zab_password_email').replace(' ', '')
            zab_new_password_1 = st.text_input("Новий пароль", type='password',key='zab_new_password_1').replace(' ', '')
            zab_new_password_2 = st.text_input("Введіть повторно пароль", type='password',key='zab_new_password_2').replace(' ', '')
            if st.button("Замінити пароль"):
                cursor.execute("""select * from user_info where phone_number = %s and email = %s;""",(zab_password_phone_number, zab_password_email))
                zab_password_result = cursor.fetchone()
                if zab_password_result:
                    if zab_new_password_1 == zab_new_password_2:
                        cursor.execute("update auth set password = %s where login = %s;",(zab_new_password_1, zab_password_login))
                        st.succes("Пароль успішно змінено!")
                    else:
                        st.error("Паролі не збігаються!")
                else:
                    st.error("Користувача з такими даними не знайдено!")
 
    
