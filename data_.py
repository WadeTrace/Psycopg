from pprint import pprint
import psycopg2

with psycopg2.connect(database="data_base", user="postgres", password="2233223323a") as conn:
    with conn.cursor() as cur:
        def create_db(conn):
            with conn.cursor() as cur:
                cur.execute("""
                    DROP TABLE phone;
                    DROP TABLE client;                                    
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS client (id SERIAL PRIMARY KEY, 
                                                        name VARCHAR(60) NOT NULL,
                                                        surname VARCHAR(60) NOT NULL,
                                                        email VARCHAR(80) UNIQUE NOT NULL
                                                        CONSTRAINT check_valid_email CHECK
                                                            (email ILIKE '%@gmail.com' 
                                                            OR email ILIKE '%@mail.ru'));                                    
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS phone (id SERIAL PRIMARY KEY, 
                                                        client_id INTEGER NOT NULL REFERENCES client(id),
                                                        number VARCHAR(50) UNIQUE NOT NULL 
                                                        CONSTRAINT check_valid_number CHECK
                                                        (number ~ '^[7]{1}[0-9]{10}?$'
                                                        ));                                    
                """)

                conn.commit()


        def find_client(conn, name=None, surname=None, email=None, phone=None):
            with conn.cursor() as cur:
                if name:
                    cur.execute("""
                                SELECT name, surname, email, number FROM client c
                                LEFT JOIN phone p ON c.id = p.client_id
                                WHERE name ILIKE %s;     
                                """, (name,))
                elif surname:
                    cur.execute("""
                                SELECT name, surname, email, number FROM client c
                                LEFT JOIN phone p ON c.id = p.client_id
                                WHERE surname ILIKE %s;     
                                """, (surname,))
                elif email:
                    cur.execute("""
                                SELECT name, surname, email, number FROM client c
                                LEFT JOIN phone p ON c.id = p.client_id
                                WHERE email ILIKE %s;     
                                """, (email,))
                elif phone:
                    cur.execute("""
                                SELECT name, surname, email, number FROM client c
                                LEFT JOIN phone p ON c.id = p.client_id
                                WHERE number = %s;     
                                """, (phone,))

                pprint(cur.fetchall())


        class Client:
            def __init__(self, conn, name, surname, email, phone=None):
                self.name = name
                self.surname = surname
                self.email = email
                self.phone = phone
                with conn.cursor() as cur:
                    cur.execute("""
                                INSERT INTO client(name, surname, email) VALUES
                                (%s, %s, %s);
                            """, (self.name, self.surname, self.email))

                    cur.execute("""
                                SELECT id FROM client 
                                WHERE email = %s;
                            """, (self.email,))
                    self.client_id = cur.fetchone()[0]

                    if phone:
                        cur.execute("""
                                    INSERT INTO phone(number, client_id) VALUES
                                    (%s, (SELECT c.id FROM client c WHERE email = %s LIMIT 1));
                                """, (self.phone, self.email))
                    conn.commit()

            def add_phone(self, conn, phone):
                with conn.cursor() as cur:
                    cur.execute("""
                                INSERT INTO phone(number, client_id) VALUES
                                (%s, %s);
                            """, (phone, self.client_id))

                    conn.commit()

            def change_client_info(self, conn, name=None, surname=None, email=None, phone=None, phone_to_change=None):
                with conn.cursor() as cur:
                    if phone and phone_to_change:
                        cur.execute("""
                                    UPDATE phone p SET number=%s 
                                    WHERE p.number=%s AND client_id=%s;     
                                """, (phone, phone_to_change, self.client_id))

                    if name:
                        cur.execute("""
                                    UPDATE client c SET name=%s WHERE id=%s;     
                                """, (name, self.client_id))

                    if surname:
                        cur.execute("""
                                    UPDATE client c SET surname=%s WHERE id=%s;     
                                """, (surname, self.client_id))

                    if email:
                        cur.execute("""
                                    UPDATE client c SET email=%s WHERE id=%s;     
                                """, (email, self.client_id))

                    conn.commit()

            def del_phone(self, conn, phone):
                with conn.cursor() as cur:
                    cur.execute("""
                                DELETE FROM phone WHERE number=%s AND client_id=%s;     
                                """, (phone, self.client_id))

                    conn.commit()

            def del_client(self, conn):
                with conn.cursor() as cur:
                    cur.execute("""
                                DELETE FROM phone WHERE client_id=%s;     
                                """, (self.client_id,))

                    cur.execute("""
                                DELETE FROM client WHERE id=%s;     
                                """, (self.client_id,))

                    conn.commit()


        def test(conn):
            create_db(conn)
            client1 = Client(conn, "Dima", "Pozharskiy", "alex@gmail.com", "79999999987")
            client2 = Client(conn, "Alena", "Suhaya", "mya@mail.ru", "79111111111")

            client1.add_phone(conn, '79888888889')
            client2.add_phone(conn, '71111111177')

            client1.change_client_info(conn, phone='79781117733', phone_to_change='79781117722')
            client2.change_client_info(conn, name='Sasha', surname='Prosto', email='kau@mail.ru', phone='79781123125',
                                       phone_to_change='79111111111')

            client1.del_phone(conn, "79999999987")



            find_client(conn, name="Dima")
            find_client(conn, phone="71111111177")
            find_client(conn, name='Sasha', phone='79781123125')


test(conn)
conn.close()
