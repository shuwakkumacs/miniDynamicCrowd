#mysql -u root -proot -Bse "CREATE USER $MYSQL_USERNAME@'myadmin.dcnet' IDENTIFIED BY '$MYSQL_PASSWORD';"
sudo sed -i "s/bind-address/#bind-address/" /etc/mysql/mysql.conf.d/mysqld.conf;
service mysql restart;

cd ~/DynamicCrowd; python manage.py makemigrations;
