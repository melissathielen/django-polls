addEvent('domready', function () {
    $$('.poll-to-load').each(function (el) {
        var pollId = el.get('data-poll-id');
        
        //Display the poll within the div
        var pollRequest = new Request.HTML({
            url: '/polls/' + pollId + '/',
            update: el,
            method: 'get',
            onSuccess: function () {
                //Add functionality for Poll Form
                pollFormVoting(el, pollId, pollRequest);
                //Add functionality for View Results Link
                viewResults(el, pollId, pollRequest);
            }
        });
        pollRequest.send();
    });
    
    //Display the voting form within div (el)
    var pollFormVoting = function (el, pollId, pollRequest) {
        var pollForm = $('poll-form');
        if (pollForm) {
            pollForm.addEvent('submit', function (evt) {
                evt.stop();
                var voteRequest = new Request.HTML({
                    url: '/polls/' + pollId + '/',
                    update: el,
                    onSuccess: function () {
                        backToPoll(pollRequest);
                        pollFormVoting(el, pollId, pollRequest);
                        viewResults(el, pollId, pollRequest);
                    }
                });
                voteRequest.post(pollForm);
            });
        };
    };
    
    //Display the view results within the div (el)
    var viewResults = function (el, pollId, pollRequest) {
        var resultsLink = $('view-results-link');
        if (resultsLink) {
            resultsLink.addEvent('click', function (evt) {
                evt.stop();
                var resultsRequest = new Request.HTML({
                    url: '/polls/' + pollId + '/results/',
                    update: el,
                    method: 'get',
                    onSuccess: function () {
                        backToPoll(pollRequest);
                    }
                });
                resultsRequest.send();
            });
        }
    };
    
    //Display the back to poll link within the div
    var backToPoll = function (pollRequest) {    
        var backToPollLink = $('back-to-poll-link');
        if (backToPollLink) {
            backToPollLink.addEvent('click', function (evt) {
                evt.stop();
                pollRequest.send();
            });
        }
    };
    
    //Script for removing number of selections allowed dropdown,
    //unless the allow multiple selections box is checked
    pollEditForm = $('create-poll-form');
    if (pollEditForm) {
        allow_multiple_selections = $('id_allow_multiple_selections');
        number_selections_allowed = $('id_number_selections_allowed');
        if (allow_multiple_selections) {
            
            if (allow_multiple_selections.checked) {
                number_selections_allowed.style.display = '';                
            } else {
                number_selections_allowed.style.display = 'none'; 
            }
            
            allow_multiple_selections.addEvent('click', function (evt) {
                if (allow_multiple_selections.checked) {
                    number_selections_allowed.style.display = '';
                } else {
                    number_selections_allowed.style.display = 'none';
                }
            });
        }
    }
});