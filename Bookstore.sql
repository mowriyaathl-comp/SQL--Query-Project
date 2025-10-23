use kanidb;
create table books(id int,title varchar(100),author varchar(50),publication_year int,genre varchar(50),price decimal(10,2),stock int);
insert into books values(1,'To kill a mockingbird','harper lee',1960,'fiction',12.99,10),
(2,1984,'George orwell',1949,'science fiction',10.99,15),
(3,'pride and prejudice','Jane austen',1813,'romance',9.99,5),
(4,'The hobbit','J.R.R Tolkien',1937,'fantasy',14.99,20),
(5,'The Catcher in the Rye','J.D.Salinger',1951,'fiction',11.99,8);
select*from books;
select sum(price*stock) as total_inventory_value from books; 

select genre, count(*) as book_count from books group by genre;

SET SQL_SAFE_UPDATES=0;
select title,price as original_price,round(price*0.9,2) as new_price from books where publication_year<1950;
update books set price=round(price*0.9,2) where publication_year<1950;

select title,author,genre,price from books where genre='fiction'or price<12;

select title,stock as days_to_sell_all from books where stock>10 order by days_to_sell_all desc;



