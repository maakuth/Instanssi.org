# -*- coding: utf-8 -*-

from operator import itemgetter

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.misc.time_formatting import compo_times_formatter
from Instanssi.kompomaatti.models import Entry, Compo, Vote

def compolist(request):
    # Get compos, format times
    composet = Compo.objects.filter(active=True).order_by('compo_start')
    compos = []
    for compo in composet:
        compos.append(compo_times_formatter(compo))
    
    # Get entries in compos. If compo has been flagged to show voting results, 
    # then get those. Otherwise just show entries in alphabetical order (by entry name).
    entries = {}
    for compo in compos:
        if compo.show_voting_results:
            # Get entries
            entries_temp = {}
            for entry in Entry.objects.filter(compo=compo):
                entries_temp[entry.id] = {
                    'id': entry.id,
                    'creator': entry.creator,
                    'name': entry.name,
                    'score': 0.0,
                    'disqualified': entry.disqualified,
                }
                # Want to show disqualified entries dead last.
                if entry.disqualified:
                    entries_temp[entry.id]['score'] = -1.0
            
            # Get score for each entry. Score should be 0 for all disqualified entries, 
            # so just discard those. Also skip votes with rank = 0. (division by zero etc.) :P
            all_votes = Vote.objects.select_related(depth=1).filter(compo=compo)
            for vote in all_votes:
                if not vote.entry.disqualified or vote.rank > 0:
                    entries_temp[vote.entry.id]['score'] += (1.0 / vote.rank)
            
            # Sort entries by score, highest score first (of course).
            entries[compo.id] = sorted(entries_temp.values(), key=itemgetter('score'), reverse=True)
        else:
            # Just get entries in alphabetical order
            entries[compo.id] = Entry.objects.filter(compo=compo).order_by('name')

    # Return page
    return custom_render(request, 'kompomaatti/compolist.html', {
        'compolist': compos,
        'entries': entries
    })