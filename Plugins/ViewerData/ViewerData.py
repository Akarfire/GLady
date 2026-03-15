import Plugin as PluginAPI

import sqlite3
from pathlib import Path

class ViewerData(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)

        # Registering event processor function for later mapping configuration
        self.eventProcessingFunctions["AppendViewerData"] = self.append_viewer_data
        self.eventProcessingFunctions["ModifyViewerData"] = self.modify_viewer_data
        #...
        
        # Defining default options
        self.defaultOptions : dict = {
            "DatabasePath" : "./Resources/ViewerData/ViewerData.db",
            "DataColumns" : {
                "NameColor" : {"type" : "TEXT", "default" : "Random"}, 
                "MessageCount" : {"type" : "INTEGER", "default" : 0}
                }
        }
        
        self.databaseConnection : sqlite3.Connection = None
        self.cursor : sqlite3.Cursor = None
        
        self.select_columns_str : str = "UserName"
     
     
    # Performs a fetchall on the cursor and reformats it into a list if dictionaries <ColumnName : Value>
    def __fetchall_dict(self) -> list[dict[str, any]]:
        out_list = []   

        fetch_result = self.cursor.fetchall()
        for row in fetch_result:
            out_dict = {}
            
            out_dict["UserName"] = row[0]
            
            column_names = [i for i in self.get_option("DataColumns")]
            for i in range(1, len(row)):
                out_dict[column_names[i - 1]] = row[i]
            
            out_list.append(out_dict)
            
        return out_list
       

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        
        # Ensures that database directory exists
        directory_path = Path(self.get_option("DatabasePath")).parent
        directory_path.mkdir(exist_ok=True, parents=True)
        
        # Connecting to the database
        self.databaseConnection = sqlite3.connect(self.get_option("DatabasePath"))
        self.cursor = self.databaseConnection.cursor()
        
        # Creating a table if it does not exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ViewerData (
        UserName TEXT NOT NULL PRIMARY KEY
        );
        ''')
        self.databaseConnection.commit()
        
        super().load()
        
     
    def reload_config(self):
        super().reload_config()  
        
        # Fetching column names
        self.cursor.execute(f"PRAGMA table_info('ViewerData')")
        columns = [row[1] for row in self.cursor.fetchall()]
        
        # Columns configuration
        columns_config : dict[str, str] = self.get_option("DataColumns")
        
        # Checking if columns exist and creating them if not
        for column in columns_config:
            if not column in columns:
                self.cursor.execute(f'''
                    ALTER TABLE ViewerData 
                    ADD COLUMN {column} {columns_config[column]["type"]}
                    DEFAULT ?;
                ''', (columns_config[column]["default"],))
                
        self.databaseConnection.commit()
        
        self.select_columns_str = "UserName"
        for column in columns_config:
            self.select_columns_str += f", {column}"
        

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()
        self.databaseConnection.close()
        
    # Called every core's main loop update
    def update(self, delta_time : float):
        super().update(delta_time)


    # Appends viewer data from the database to the event
    def append_viewer_data(self, event : PluginAPI.Event, arguments : dict = {}):

        user_name = ""
        if "UserName" in event.data:
            user_name = event.data["UserName"]
            
        if "UserName" in arguments:
            user_name = arguments["UserName"]
            
        if user_name == "": raise Exception("No 'UserName' is specified")
        
        # Registering a new db entry if it does not exist yet
        self.cursor.execute("INSERT OR IGNORE INTO ViewerData (UserName) VALUES (?);", (user_name,))
        self.databaseConnection.commit()
        
        self.cursor.execute(f"SELECT {self.select_columns_str} FROM ViewerData WHERE UserName = ?;", (user_name,))
        data = self.__fetchall_dict()
        
        if len(data) == 0 : return
        user_data = data[0]
        
        # Saturating the event's data with viewer data
        for entry in user_data:
            event.data[entry] = user_data[entry]
     
        
    # Modifies viewer data
    # arguments must contain "NewValues" : {"ValueName" : "SET Operation"}
    # alternatively you can pass it in event.data as "ViewerData_NewValues"
    def modify_viewer_data(self, event : PluginAPI.Event, arguments : dict = {}):
        
        # User name
        user_name = ""
        if "UserName" in event.data:
            user_name = event.data["UserName"]
            
        if "UserName" in arguments:
            user_name = arguments["UserName"]
            
        if user_name == "": raise Exception("No 'UserName' is specified")
        
        # Registering a new db entry if it does not exist yet
        self.cursor.execute("INSERT OR IGNORE INTO ViewerData (UserName) VALUES (?);", (user_name,))
        
        # New Values
        new_values = {}
        if "ViewerData_NewValues" in event.data:
            new_values = event.data["ViewerData_NewValues"]
            
        if "NewValues" in arguments:
            new_values = arguments["NewValues"]
            
        for value in new_values:
            if value in self.get_option("DataColumns"):
                self.cursor.execute(f"UPDATE ViewerData SET {value} = {new_values[value]} WHERE UserName = ?", 
                    (user_name,))
                
        self.databaseConnection.commit()
        
            
        

