import express from 'express';
import dbBase from './src/getDB.js'
import logger from './src/logger.js'
import {escapeUser, escapeNumber, escapeRelationShipConstraints} from './src/escapeInputs.js'
import { GitNode } from './src/model/gitNode.mjs';
import { GitEdge } from './src/model/gitEdge.mjs';
import cors from 'cors';
const app = express()
const port = 3000

const dbDriver = await dbBase.getDB()
app.use(cors());
app.use(logger.logger);


app.get('/getDistance', (req, res) => {
    let relConstraint = '';
    let minDist = (req.query['minDist'] != undefined) ? escapeNumber(req.query['minDist']) : 1
    let maxDist = (req.query['maxDist'] != undefined) ? escapeNumber(req.query['maxDist']) : 10
    let typeStart = req.query['typeStart'] == undefined ? 'User' : req.query['typeStart'];
    let typeEnd = req.query['typeEnd'] == undefined ? 'User' : req.query['typeEnd'];
    if (!['User', 'Repo'].includes(typeStart) || !['User', 'Repo'].includes(typeEnd)
        || req.query['start'] == undefined
        || req.query['end'] == undefined) {
        res.status(400)
        res.send("invalid parameter")
        return;
    }
    if(req.query['relationShipConstraints'] != undefined){
        relConstraint = ':' + escapeRelationShipConstraints(req.query['relationShipConstraints'])
    }
    let session = dbDriver.session();
    session.executeRead( async tx => {
        const txString = `MATCH path=SHORTESTPATH(
            (p:${typeStart}{name: '${escapeUser(req.query['start'])}'})
            -[rel${relConstraint}*${minDist}..${maxDist}]-
            (tar:${typeEnd}{name:'${escapeUser(req.query['end'])}'})) 
            RETURN path`
        console.log(txString)
        const path = await tx.run(txString);
        res.send(path.records)
    }).then(() => session.close());
})

// gets all nodes connected to a user up to a certain distance
app.get('/getRelatives', (req, res) => {
    let relConstraint = '';
    let minDist = (req.query['minDist'] != undefined) ? escapeNumber(req.query['minDist']) : 1
    let maxDist = (req.query['maxDist'] != undefined) ? escapeNumber(req.query['maxDist']) : 1
    let type = ''
    type = req.query['type'] == undefined ? 'User' : req.query['type'];
    if ( req.query['start'] == undefined || !(type=='User' || type=='Repo')){
        res.status(400)
        res.send("invalid parameter")
        return;
    }
    if (req.query['relationShipConstraints'] != undefined){
        relConstraint = ':' + req.query['relationShipConstraints']
    }
    let session = dbDriver.session();
    session.executeRead( async tx => {
        // type does not need to be escaped, because it can only be User or Repo (checked above)
        const txString = `MATCH (source:${type}{name: '${escapeUser(req.query['start'])}'})-[rel${relConstraint}*${minDist}..${maxDist}]-(dest) RETURN collect(distinct source), collect(distinct dest), collect(distinct rel)`
        const result = await tx.run(txString);
        const nodes = [];
        const rel = [];
        result.records[0]._fields[0].forEach(element => {
            nodes.push(new GitNode(element.properties.name, element.properties.avatar ? element.properties.avatar : "", element.labels[0], element.identity.low))
        });
        result.records[0]._fields[1].forEach(element => {
            nodes.push(new GitNode(element.properties.name, element.properties.avatar ? element.properties.avatar : "", element.labels[0], element.identity.low))
        })
        result.records[0]._fields[2].forEach(element => {
            element.forEach( innerElement => {
                rel.push(new GitEdge(innerElement.start.low , innerElement.end.low, innerElement.identity.low, innerElement.type, innerElement.properties.weight ? innerElement.properties.weight : -1))
            })
        })
        res.send({nodes, rel});
    })
    .then(() => session.close()) 

})

app.get('/nodeStats', (req, res) => {
    let type = req.query['type'] == undefined ? 'User' : req.query['type'];
    if(req.query['node'] == undefined || !(type =='User' || type=='Repo')){
        res.status(400)
        res.send("invalid or missing parameter detected");
    }
    let session = dbDriver.session()
    session.executeRead (async tx => {
        const txString = `MATCH (p:${type}{name:'${escapeUser(req.query['node'])}'})-[r]-() RETURN TYPE(r) as type, COUNT(r) as amount`
        console.log("executing query: " + txString)
        const result = await tx.run(txString);
        res.send(result.records)
    })
    .then(() => {session.close()})
})

// gets general facts about the database
app.get('/stats', (req, res) =>{
    let session = dbDriver.session();
    session.executeRead( async tx => {
        const nodeCount = await tx.run('MATCH (p) RETURN COUNT(p)')
        const relationshipCount = await tx.run('MATCH () -[r]-> () RETURN COUNT(r);')
        res.send('node count: ' + nodeCount.records[0]._fields[0].low + '<br/> relationship count: ' + relationshipCount.records[0]._fields[0].low)
    }).then(() => session.close())
    
})


app.listen(port, () => {
    console.log(`listening on port ${port}`)
})


