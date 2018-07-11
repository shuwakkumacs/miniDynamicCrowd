mysql -u root -proot -Bse "CREATE USER $MYSQL_USERNAME@'myadmin.dcnet' IDENTIFIED BY '$MYSQL_PASSWORD';"
mysql -u $MYSQL_USERNAME -p$MYSQL_PASSWORD -Bse "DROP USER root@'localhost';"
sudo sed -i "s/.*bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.conf;
service mysql restart;
