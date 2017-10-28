import argparse
import subprocess
import sys
from termcolor import colored
from extractor.xtorrent import XTorrent
from extractor.yts import yts
from extractor.eztv import eztv
#%%

from urllib.parse import quote_plus

def cmd_exists(cmd):
    return subprocess.call('type ' + cmd, shell=True, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE) == 0


def peerflix(title, magnet_link, media_player, media_type):
    is_audio = '-a' if media_type == 'music' else ''
    print('Playing %s!' % title)
    subprocess.Popen(['/bin/bash', '-c', 
                      'peerflix "{0}" {1} --{2}'.format(magnet_link, 
                                                        is_audio, 
                                                        media_player)])


def parser():
    p = argparse.ArgumentParser()
    p.add_argument('media_type', choices=['movie', 'tv', 'music'])
    p.add_argument('query')
    p.add_argument('source', nargs='?',default='0')
    p.add_argument('latest', nargs='?', default='0')
    
    return p.parse_args()


def search():
    query = input('Enter the search query: (media-type query)')
    query = query.split()
    if len(query) >= 2:
        main(media_type=query[0], q=' '.join(query[1:]))
    else:
        search()




def main(q=None, media_type=None):
    args = parser()
    query = args.query if q is None else q
    media_type = args.media_type if media_type is None else media_type
    source = args.source 
    media_player = 'mpv'
    need_magnet = False
    found = False
    torrents = []
    xt = []
    #
    try:
        
        assert source == '0'
        xt = XTorrent(quote_plus(query), media_type)
        torrents = xt.get_torrents()
        print("\n\nUsing XTorrent\n\n")
        need_magnet = True
        assert len(torrents) >0   
    except:
        try: 
            if media_type == 'tv':
                print("\n\nUsing EZTV \n\n")
                torrents = eztv(query.replace(' ', '-').lower())
            elif media_type == 'movie':
                print("\n\nUsing YTS \n\n")
                torrents = yts(quote_plus(query))         
            assert len(torrents) >0    
        except:
            sys.exit(colored('No results found.', 'red'))
    ## Get the torrents. 
    if args.latest == 'latest':
        
        if need_magnet:
            torrents = xt.get_magnet(1)
            if torrents:
                peerflix(torrents[0], torrents[1], media_player, media_type)
            else:
                latest = torrents[0]
                peerflix(latest['title'], latest['magnet'], media_player, media_type)

    else:
        
        print('Select %s' % media_type.title())
        #%%
        for result in torrents:
            print(colored("| {id} |\t {title}".format(**result), attrs=["bold"]))
        #%%
        while True:
            read = input()

            if read == 'quit':
                sys.exit()
            

            try:
                val = int(read)
            except ValueError:
                print(colored('Expected int.','red'))
                continue

            if need_magnet:
                torrents = xt.get_magnet(val)
                if torrents:
                    found = True
                    
                    peerflix(torrents[0], torrents[1], media_player, media_type)
                else:
                    found = False

            else:
                for result in torrents:
                    if result['id'] == int(read):
                        found = True
                        peerflix(result['title'], result['magnet'], media_player, media_type)

            if not found:
                print(colored('Invalid selection.', 'red'))


if __name__ == '__main__':
    try:
        if not cmd_exists('peerflix'):
            sys.exit('This program requires Peerflix. https://github.com/mafintosh/peerflix')
        if not cmd_exists('mpv'):
            print('MPV not found. Setting default player as vlc.')
            player = 'vlc'
        main()
    except KeyboardInterrupt:
        sys.exit()
