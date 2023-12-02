let escapeUser = (username) => {
    username = username.replace("\\", "\\\\")
    username = username.replace("'", "\\'")
    username = username.replace('"', '\\"')
    console.log("escaped string: " +username)

    return username;
}

let escapeNumber = (numberString) => /^\d+$/.test(numberString) ? numberString : '1';

let escapeRelationShipConstraints = (constraint) => {
    constraint = constraint.replace("\\", "\\\\")
    constraint = constraint.replace("'", "\\'")
    constraint = constraint.replace('"', '\\"')
    constraint = constraint.replace(" ", "")
    return constraint
}

module.exports = {escapeUser: escapeUser, escapeNumber:escapeNumber, escapeRelationShipConstraints: escapeRelationShipConstraints}

/*
queries to test escaping
user='}) RETURN 1 UNION MATCH (n) RETURN 1 //
maxDist=2d

*/