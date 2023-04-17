SELECT DISTINCT people.name
FROM stars
JOIN people ON people.id = stars.person_id
JOIN (
    SELECT movie_id
    FROM stars
    JOIN people ON people.id = stars.person_id
    WHERE people.name = 'Kevin Bacon' AND people.birth = 1958
) AS kb_movies ON kb_movies.movie_id = stars.movie_id
WHERE people.name != 'Kevin Bacon'
;