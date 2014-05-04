
function getDatabase() {
    return openDatabaseSync("meegoodfet", "0.1", "StorageDatabase", 100000);
}


function initialize() {
    var db = getDatabase();
    db.transaction(
                function(tx) {
                    tx.executeSql('CREATE TABLE IF NOT EXISTS settings(setting TEXT UNIQUE, value TEXT)');
                });
}

function setSetting(setting, value) {
    var db = getDatabase();
    var res = "";
    db.transaction(function(tx) {
                       var rs = tx.executeSql('INSERT OR REPLACE INTO settings VALUES (?,?);', [setting,value]);
                       return(rs.rowsAffected>0);
                   }
                   );
    return res;
}

function getSetting(setting) {
    var db = getDatabase();
    var res="";
    db.transaction(function(tx) {
                       var rs = tx.executeSql('SELECT value FROM settings WHERE setting=?;', [setting]);
                       if(rs.rows.length>0)
                           res = rs.rows.item(0).value;
                       else
                           res = "Unknown";

                   });
    return res
}
