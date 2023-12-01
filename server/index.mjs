
import express from 'express';
import dbBase from './src/getDB.js'
import logger from './src/logger.js'
const app = express()
const port = 3000

const dbDriver = await dbBase.getDB()
app.use(logger.logger);

app.get('/getUserDistance', (req, res) => {

  res.send('Hello World!')
})

app.get('/getRepoDistance', (req, res) => {
    res.send('');
})

// gets all nodes connected to a user up to a certain distance
app.get('/getUserRelatives', (req, res) => {
    let session = dbDriver.session();
    let relConstraint = '';
    let minDist = (req.query['minDist'] != undefined) ? req.query['minDist'] : 1;
    let maxDist = (req.query['maxDist'] != undefined) ? req.query['maxDist'] : 1
    console.log(req.query)
    if (req.query['user'] == undefined){
        res.status(400)
        res.send("invalid parameter user")
        return;
    }
    if (req.query['relationShipConstraints'] != null && req.query['relationShipConstraints'] != undefined){
        relConstraint = ':' + req.query['relationShipConstraints']
    }
    session.executeRead( async tx => {
        const nodes = await tx.run(`MATCH (source:User{name: '${req.query['user']}'})-[rel${relConstraint}*${minDist}..${maxDist}]->(dest) RETURN source, dest, rel`);
        res.send(nodes);
        session.close();
    })

})

// gets all nodes connect to a repo up to a certain distance
app.get('/getRepoRelatives', (req, res) => {
    
})

// gets general facts about the database
app.get('/stats', (req, res) =>{
    let session = dbDriver.session();
    session.executeRead( async tx => {
        const nodeCount = await tx.run('MATCH (p) RETURN COUNT(p)')
        const relationshipCount = await tx.run('MATCH () -[r]-> () RETURN COUNT(r);')
        res.send('node count: ' + nodeCount.records[0]._fields[0].low + '<br/> relationship count: ' + relationshipCount.records[0]._fields[0].low)
        session.close()
    })
    
})


app.listen(port, () => {
    console.log(`listening on port ${port}`)
})


