SELECT m.title
FROM movies m
INNER JOIN stars s1 ON s1.movie_id = m.id
INNER JOIN people p1 ON p1.id = s1.person_id AND p1.name = 'Johnny Depp'
INNER JOIN stars s2 ON s2.movie_id = m.id
INNER JOIN people p2 ON p2.id = s2.person_id AND p2.name = 'Helena Bonham Carter'
;
