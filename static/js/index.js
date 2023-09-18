
/**
 * 
 * @param {SubmitEvent} event 
 */
function handleQuery(event) {
    event.preventDefault();
    let queryText = event.target.elements.query.value;
    console.log(queryText);
    fetch('./search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({search: queryText})
    }).then(response => response.json()).then(data => generateLinks(data))
};


/**
 * 
 * @param {json} data 
 * @returns none
 */
function generateLinks(data) {
    let results = document.querySelector('.content');
    results.innerHTML = ''
    data.forEach(element => {
        let li = document.createElement('li');
        let link = document.createElement('a')
        link.href = element
        link.textContent = element
        li.appendChild(link)
        results.appendChild(li);
    });
    console.log(results);
};

let userInput = document.getElementById('search');
userInput.addEventListener('submit', handleQuery);