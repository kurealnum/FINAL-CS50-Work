select title from people
join stars on people.id = stars.person_id
join movies on movies.id = stars.movie_id
join ratings on movies.id = ratings.movie_id
where people.name = "Chadwick Boseman"
order by ratings.rating desc
limit 5
;

