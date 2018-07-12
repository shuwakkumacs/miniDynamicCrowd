#!/bin/bash

# mysql
chown -R mysql:mysql /var/lib/mysql /var/run/mysqld
service mysql start;
if [ -n "${MYSQL_USERNAME}" ] && [ -n "${MYSQL_PASSWORD}" ]; then
  mysql -u root -proot -Bse "CREATE USER $MYSQL_USERNAME@'myadmin.dcnet' IDENTIFIED BY '$MYSQL_PASSWORD';"
  mysql -u root -proot -Bse "GRANT ALL PRIVILEGES ON *.* TO $MYSQL_USERNAME@'myadmin.dcnet'"
fi
sed -i "s/^bind-address/#bind-address/" /etc/mysql/mysql.conf.d/mysqld.cnf;
service mysql restart;

# settings/global.json
cp /root/DynamicCrowd/settings/global.json.default /root/DynamicCrowd/settings/global.json
if [[ -n "${BASE_URL}" ]]; then
  sed -i "s@\"BaseUrl.*@\"BaseUrl\"\: \"$BASE_URL\",@" /root/DynamicCrowd/settings/global.json;
fi
if [[ -n "${AWS_ACCESS_KEY_ID}" ]]; then
  sed -i "s/\"AWSAccessKeyId.*/\"AWSAccessKeyId\"\: \"$AWS_ACCESS_KEY_ID\",/" /root/DynamicCrowd/settings/global.json;
fi
if [[ -n "${AWS_SECRET_ACCESS_KEY}" ]]; then
  sed -i "s/\"AWSSecretAccessKey.*/\"AWSSecretAccessKey\"\: \"$AWS_SECRET_ACCESS_KEY\"/" /root/DynamicCrowd/settings/global.json;
fi

# database migration
cd ~/DynamicCrowd; python manage.py makemigrations;

/bin/bash
