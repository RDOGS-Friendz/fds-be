\COPY location(name) FROM './data_collection/location.csv' DELIMITER ',' CSV HEADER;
\COPY category(name) FROM './data_collection/category.csv' DELIMITER ',' CSV HEADER;
\COPY department(school, department_name) FROM './data_collection/department.csv' DELIMITER ',' CSV HEADER;