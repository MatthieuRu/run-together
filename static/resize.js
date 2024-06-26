//// assets/resize.js
//window.addEventListener('resize', function(event) {
//    const graphs = document.getElementsByClassName('dash-graph');
//    for (let i = 0; i < graphs.length; i++) {
//        graphs[i].dispatchEvent(new Event('resize'));
//    }
//});
//
// assets/resize.js
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        storeWindowSize: function(interval) {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        }
    }
});