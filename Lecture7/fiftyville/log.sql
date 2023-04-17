-- Keep a log of any SQL queries you execute as you solve the mystery.

-- find the theif and their id, then "cross reference" that to any calls that id/name made, and that's probably the accomplice

select * from crime_scene_reports;

select * from bakery_security_logs;

select * from bakery_security_logs where day = 28 and month = 7 and year = 2021;

select * from crime_scene_reports where day = 28 and month = 7 and year = 2021 and street = "Humphrey Street";

-- transcripts with full info

select * from interviews where day = 28 and month = 7 and year = 2021;

-- accomplice could be a bakery worker, barbara (160) was a prime witness. also eugene (162).
-- theif took the earliest flight, and the accomplice purchased the flight ticker
-- accomplice/theif could be german, if that helps
-- theif drove away within ten minutes of the theft (between 10:15 - 10:25am)

-- i was so wrong here lmao

select minute from bakery_security_logs;

select * from bakery_security_logs where minute = 25 and day = 28 and month = 7 and year = 2021;

-- license_plate is either L68E5I0 or HOD8639, probably the latter

select * from bakery_security_logs
    join people on people.license_plate = bakery_security_logs.license_plate
        where bakery_security_logs.license_plate = "L68E5I0" or "HOD8639"
        and day = 28;

select * from people where license_plate = "HOD8639";

-- getting people and license plates that withdrew money between 10:15-10:25
select * from bakery_security_logs b
    join atm_transactions atm on atm.id = b.id
        where b.minute between 15 and 25 and hour = 10
        and b.day = 28 and b.month = 7 and
        b.year = 2021 and activity = "exit";

-- getting people and license plates that were at the bakery between 10:15-10:25
select name, people.license_plate, activity, people.id from people
    join bakery_security_logs on bakery_security_logs.license_plate = people.license_plate
        where minute between 15 and 25 and hour = 10 and day = 28 and month = 7 and year = 2021;

-- look for cars that left
-- check calls

-- checking for atm withdrawls, assuming that Humphrey Lane is the same thing
select * from atm_transactions
    where day = 28 and month = 7 and year = 2021
    and atm_location = "Humphrey Lane" and transaction_type = "withdraw";

-- checking calls, the call was for less than a minute,
-- and he shouldve called somepoint after leaving the bakery.
-- cross referencing this with people that left the bakery at around that time

-- getting airport names

select * from flights
    join airports on airports.id = flights.origin_airport_id
        and origin_airport_id = 8 and day = 29;

-- current suspects

+--------+---------------+----------+--------+
|  name  | license_plate | activity |   id   |
+--------+---------------+----------+--------+
| Bruce  | 94KL13X       | exit     | 686048 |
| Sofia  | G412CB7       | exit     | 398010 |
| Diana  | 322W7JE       | exit     | 514354 |
| Kelsey | 0NTHK55       | exit     | 560886 |
+--------+---------------+----------+--------+

-- ACTUAL ANSWERS/SOLUTIONS

-- The THIEF is:

select distinct name, p.license_plate, p.id, p.passport_number, p.phone_number from people p
    join bakery_security_logs b on b.license_plate = p.license_plate
        and b.minute between 15 and 25 and b.hour = 10 and b.day = 28
        and b.month = 7 and b.year = 2021
    join phone_calls c on p.phone_number = c.caller and duration < 60
    join passengers a on a.passport_number = p.passport_number
    join flights f on f.id  = a.flight_id
        and f.origin_airport_id = 8 and f.day = 29 and f.hour = 8 and f.minute = 20
    join bank_accounts n on n.person_id = p.id;

-- The city the thief ESCAPED TO is:

select * from airports a
    join flights f on f.destination_airport_id = a.id
        and f.origin_airport_id = 8
    join passengers p on f.id = p.flight_id and p.passport_number = 5773159633;

-- The ACCOMPLICE is:

select distinct p.caller, p.receiver, e.name from phone_calls p
    join people e on e.phone_number = p.receiver
        where p.caller = "(367) 555-5533" and p.year = 2021 and p.month = 7 and p.day = 28
        and p.duration < 60;