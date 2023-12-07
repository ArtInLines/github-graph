require('dotenv').config()
const neo4j = require('neo4j-driver');

module.exports = {getDB: async () => {
    const db = neo4j.driver('bolt://[2001:7c0:2320:2:f816:3eff:fe96:7b16]:7687', neo4j.auth.basic(process.env.NEO4J_USER, process.env.NEO4J_PASS))
    const dbInfo = await db.getServerInfo()
    console.log("connected to db")
    console.log(dbInfo)
    return db
} }
