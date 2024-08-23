# remove previous work
DROP USER 'jordan'@'localhost';
DROP DATABASE icst;

# create db
create database icst character set utf8 collate utf8_bin;

USE icst;
START TRANSACTION;

# create table
CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(80) NOT NULL,
  `pass_hash` varchar(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

# insert admin pass record
INSERT INTO `admin` (`id`, `username`, `pass_hash`) VALUES
(1, 'admin', '$2b$12$tAf68hxb2Z0xpTE9i2wbNusRMV3tOFLLVEKx.XjMVUwBmwGmc60mq');

# set up keys
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);
  
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

# create user and grant permissions
create user 'jordan'@'localhost' identified by 'icst';
grant all privileges on icst.* to 'jordan'@'localhost';
flush privileges;