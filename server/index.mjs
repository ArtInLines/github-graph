
import express from 'express';
import dbBase from './src/getDB.js'
import logger from './src/logger.js'
import {escapeUser, escapeNumber, escapeRelationShipConstraints} from './src/escapeInputs.js'
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
app.get('/getRelatives', (req, res) => {
    let session = dbDriver.session();
    let relConstraint = '';
    let minDist = (req.query['minDist'] != undefined) ? escapeNumber(req.query['minDist']) : 1
    let maxDist = (req.query['maxDist'] != undefined) ? escapeNumber(req.query['maxDist']) : 1
    let type = ''
    console.log(req.query)
    type = req.query['type'] == undefined ? 'User' : req.query['type'];
    if ((type == 'User' && req.query['user'] == undefined) || (type=='Repo' && req.query['repo'] == undefined) || !(type=='User' || type=='Repo')){
        res.status(400)
        res.send("invalid parameter")
        return;
    }
    if (req.query['relationShipConstraints'] != null && req.query['relationShipConstraints'] != undefined){
        relConstraint = ':' + req.query['relationShipConstraints']
    }
    session.executeRead( async tx => {
        // type does not need to be escaped, because it can only be User or Repo (checked above)
        const txString = `MATCH (source:${type}{name: '${escapeUser(req.query[type=='User' ? 'user' : 'repo'])}'})-[rel${relConstraint}*${minDist}..${maxDist}]-(dest) RETURN source, dest, rel`
        console.log("txString: " + txString)
        const nodes = await tx.run(txString);
        res.send(nodes.records);
    })
    .then(() => session.close()) 

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


