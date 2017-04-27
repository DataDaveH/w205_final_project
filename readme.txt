
HOW TO SETUP ETL

1. Create an EC2 instance using this AMI and attach 100GB EBS volume.
	AMI Name: UCB MIDS W205 Ex2-FULL
	AMI ID: ami-d4dd4ec3
		
2. Configure inbound security rule:
	Type: All TCP
	Source: Anywhere

3. Connect to instance and run setup scripts
	fdisk -l
	mount -t ext4 <input EBS volume directoy> /data (not required for instance type 
	with premounted volume)
	chmod a+rwx /data
	wget https://s3.amazonaws.com/ucbdatasciencew205/setup_ucb_complete_plus_postgres.sh
	chmod +x ./setup_ucb_complete_plus_postgres.sh
	./setup_ucb_complete_plus_postgres.sh <input EBS volume directoy>

4. Load these Python packages
	pip install requests
	pip install datetime
	pip install json
	pip install psycopg2
	pip install googlemaps
	pip install pandas
	pip install sqlalchemy

5. Start Postgres (if not still running from installation script)
	/data/start_postgres.sh

6. Log into w205 user
	su - w205

7. Clone repository
	git clone https://github.com/keriwheatley/w205_final_project.git

8. Run tables setup script
	cd w205_final_project
	chmod +x ./setup/table_setup.sh
	./setup/table_setup.sh

9. Run initial load of data
	cd load
	python update_tables.py

10. Setup password for database (to enable connection to Tableau)
	psql -U postgres -d finalproject
	\password
	Enter new password: pass
	
	To test connection, type this into your local command line:
	psql -U postgres -d finalproject -h <public DNS from AWS>

11. Go to your local machine with Tableau pre-installed and open dashboards located in:
	/analysis/data_dashboards.twbx

12. If prompted, click `Yes` to accept the custom SQL stored in dashboard

13. Edit connections to point to your newly created public DNS (option not available 
    unless Tableau is being hosted on a server)

14. To refresh data, go to `Data > Refresh All Extracts...` and, if prompted, enter 
    password `pass`



Notes about the Cron task scheduler:

This application makes use of the built in Linux task scheduler called cron. By default, the system 
is set to check for new data from all configured sources each day at 1am sytem time. 

To change this behavior, switch to the user that ran the installation (w205), and type: 
`crontab -e`. This will bring up the user's cron file in a vim editor. Details on how to edit this 
file can be found online, or by typing: `man crontab`.

The default file will contain an entry that begins with "0 1 * * * $(pwd)/setup/runApp.sh $(pwd)"
This indicates that the task (that should not be changed) will be run at 0 minutes past hour 1 of 
every day of every week of every month of the year.

To see a list of all cron jobs that are scheduled for a user, type: `crontab -l`. If no jobs have 
been scheduled, the command will display nothing.
