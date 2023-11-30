
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
    const session = dbDriver.session();
    session.executeRead( tx => {
        tx.run('MATCH (p) RETURN COUNT(p);')
        .then(result =>{
            result.records.forEach(element => {
                console.log(element)
            });
    
        })
    })
    session.close()
    res.send('finisehd');

})

// gets all nodes connect to a repo up to a certain distance
app.get('/getRepoRelatives', (req, res) => {
    
})

// gets general facts about the database
app.get('/stats', (req, res) =>{
    const session = dbDriver.session();
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


