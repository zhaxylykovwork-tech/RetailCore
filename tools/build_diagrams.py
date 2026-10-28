"""Generate editable drawio and matching SVG/PNG views from one layout."""
from pathlib import Path
import xml.etree.ElementTree as ET
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 1920, 1320
FONT = Path('C:/Windows/Fonts/arial.ttf')
BOLD = Path('C:/Windows/Fonts/arialbd.ttf')

def node(key, x, y, w, h, lines, color='#ffffff'):
    return dict(id=key, x=x, y=y, w=w, h=h, lines=lines, color=color)

def edge(source, target, points, label, at, dashed=False):
    return dict(source=source, target=target, points=points, label=label, at=at, dashed=dashed)

def render(name, title, nodes, edges, groups, footer):
    out = ROOT / name
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (W,H), '#f6f8fc')
    d = ImageDraw.Draw(img)
    def font(size, bold=False): return ImageFont.truetype(str(BOLD if bold else FONT),size)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
      '<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="#415674"/></marker></defs>',
      f'<rect width="{W}" height="{H}" fill="#f6f8fc"/>']
    model = ET.Element('mxfile', host='app.diagrams.net')
    diagram = ET.SubElement(model,'diagram',id=name.replace('/','-'),name='Контекст')
    graph = ET.SubElement(diagram,'mxGraphModel',dx='1920',dy='1320',grid='1',gridSize='10',page='1',pageWidth=str(W),pageHeight=str(H))
    root = ET.SubElement(graph,'root')
    ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')
    def text(x,y,value,size=20,bold=False,color='#21324b'):
        d.text((x,y),value,font=font(size,bold),fill=color)
        svg.append(f'<text x="{x}" y="{y+size}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(value)}</text>')
    text(40,20,title,30,True)
    text(40,66,'RetailCore • спринт 4 • 28.10.2026 • контекст с крупными внутренними подсистемами',19)
    for i,g in enumerate(groups):
        x,y,w,h,label,color = g
        d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=color,outline='#a9b8cd',width=2)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#a9b8cd" stroke-width="2"/>')
        text(x+18,y+12,label,22,True)
        cell=ET.SubElement(root,'mxCell',id=f'group{i}',value=label,style=f'rounded=1;arcSize=2;fillColor={color};strokeColor=#a9b8cd;verticalAlign=top;align=left;spacing=18;fontSize=22;fontStyle=1;',vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    # Edges beneath boxes; hand-routed to avoid ambiguous intersections.
    for i,e in enumerate(edges):
        pts=e['points']; color='#415674'
        d.line(pts,fill=color,width=3)
        a,b=pts[-2],pts[-1]; ang=math.atan2(b[1]-a[1],b[0]-a[0])
        arr=[b,(b[0]-14*math.cos(ang-0.45),b[1]-14*math.sin(ang-0.45)),(b[0]-14*math.cos(ang+0.45),b[1]-14*math.sin(ang+0.45))]
        d.polygon(arr,fill=color)
        path='M '+' L '.join(f'{x},{y}' for x,y in pts)
        svg.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3" marker-end="url(#arrow)"'+(' stroke-dasharray="8 5"' if e['dashed'] else '')+'/>')
        label=e['label']; lx,ly=e['at']; box=d.textbbox((lx,ly),label,font=font(17));
        d.rectangle((box[0]-5,box[1]-3,box[2]+5,box[3]+3),fill='#f6f8fc')
        svg.append(f'<rect x="{lx-5}" y="{ly-1}" width="{box[2]-box[0]+10}" height="24" fill="#f6f8fc"/>')
        text(lx,ly,label,17)
        source=next(n for n in nodes if n['id']==e['source'])
        target=next(n for n in nodes if n['id']==e['target'])
        exit_x=(pts[0][0]-source['x'])/source['w']; exit_y=(pts[0][1]-source['y'])/source['h']
        entry_x=(pts[-1][0]-target['x'])/target['w']; entry_y=(pts[-1][1]-target['y'])/target['h']
        ports=f'exitX={exit_x};exitY={exit_y};exitPerimeter=0;entryX={entry_x};entryY={entry_y};entryPerimeter=0;'
        cell=ET.SubElement(root,'mxCell',id=f'e{i}',value=label,source=e['source'],target=e['target'],style='edgeStyle=none;rounded=0;endArrow=block;html=0;noLabel=1;strokeColor=#415674;fontSize=17;'+ports+('dashed=1;' if e['dashed'] else ''),edge='1',parent='1')
        geo=ET.SubElement(cell,'mxGeometry',relative='1',**{'as':'geometry'})
        array=ET.SubElement(geo,'Array',**{'as':'points'})
        for x,y in pts[1:-1]: ET.SubElement(array,'mxPoint',x=str(x),y=str(y))
    for n in nodes:
        x,y,w,h=n['x'],n['y'],n['w'],n['h']
        d.rounded_rectangle((x,y,x+w,y+h),radius=9,fill=n['color'],outline='#516780',width=2)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{n["color"]}" stroke="#516780" stroke-width="2"/>')
        for j,line in enumerate(n['lines']): text(x+16,y+14+j*29,line,21 if j==0 else 18,j==0)
        cell=ET.SubElement(root,'mxCell',id=n['id'],value='\n'.join(n['lines']),style=f'rounded=1;whiteSpace=wrap;html=0;fillColor={n["color"]};strokeColor=#516780;align=left;spacing=16;fontSize=19;',vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    for i,e in enumerate(edges):
        lx,ly=e['at']; tw=d.textlength(e['label'],font=font(17))
        c=ET.SubElement(root,'mxCell',id=f'label{i}',value=e['label'],style='text;html=0;align=left;verticalAlign=top;fontSize=17;spacing=0;fillColor=#f6f8fc;strokeColor=none;',vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(lx),y=str(ly),width=str(tw+8),height='26',**{'as':'geometry'})
    for i,line in enumerate(footer): text(40,1200+i*29,line,18)
    # Include title and notes in editable source too.
    for i,(y,lines) in enumerate([(16,[title]),(1190,footer)]):
        c=ET.SubElement(root,'mxCell',id=f'note{i}',value='\n'.join(lines),style='text;html=0;align=left;verticalAlign=top;fontSize=20;',vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x='40',y=str(y),width='1840',height='120',**{'as':'geometry'})
    svg.append('</svg>')
    out.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf-8')
    ET.indent(model)
    ET.ElementTree(model).write(out.with_suffix('.drawio'),encoding='utf-8',xml_declaration=True)
    img.save(out.with_suffix('.png'))

def main():
    n=[node('client',65,125,300,85,['Клиенты','Сайт и мобильные каналы']),node('market',470,125,290,85,['Маркетплейсы','Заказы и обновления']),node('support',1550,125,300,85,['Поддержка','Операторские сценарии']),
       node('core',470,330,600,250,['Java-монолит / write-контур','Checkout и Order Processing','Цена / промо / канальные ветки','Payment / Delivery / Status','Оркестрация остаётся в ядре'],'#fff1cb'),
       node('db',1190,350,280,150,['Oracle','Заказы, история, правила','Packages, staging, retry'],'#fff1cb'),node('admin',1550,350,300,120,['Admin / Support tools','Чтение и ручные действия','S, D1, P'],'#fff1cb'),
       node('promo',65,1035,300,105,['Promo / наличие','Sync по D1/C','Полный контракт неизвестен']),node('async',470,700,280,110,['Batch / async','Jobs, сообщения, выгрузки','Разные гарантии D2'],'#fff1cb'),
       node('net',840,700,270,110,['.NET-интеграции','Общая схема / polling','Партнёрские сценарии'],'#fff1cb'),node('python',1190,700,280,110,['Python-аналитика','SQL, API, staging, CSV','D3 / P'],'#fff1cb'),
       node('payment',470,1035,290,105,['Платёжные провайдеры','Создание сессии','Не равно списанию']),node('delivery',840,1035,340,105,['Доставка / склады','Sync / batch / broker','Исключения, дубли D2']),node('bi',1550,1035,300,105,['BI / бизнес','Отчётные запросы','Разные определения D3'])]
    e=[edge('client','core',[(215,210),(215,280),(550,280),(550,330)],'create / status • sync',(240,290)),edge('market','core',[(615,210),(615,330)],'канальные ветки',(630,290)),edge('support','admin',[(1700,210),(1700,350)],'проверка / корректировка',(1480,272)),
       edge('core','db',[(1070,410),(1190,410)],'SQL',(1095,380)),edge('admin','db',[(1550,400),(1470,400)],'тех. данные',(1465,330)),edge('core','promo',[(470,480),(405,480),(405,1085),(365,1085)],'вызов / fallback',(85,945)),
       edge('core','async',[(610,580),(610,700)],'задания / события',(620,620)),edge('db','net',[(1300,500),(1300,570),(970,570),(970,700)],'staging / INT_ORDER_EXPORT',(1095,540)),edge('async','net',[(750,750),(840,750)],'обмен',(755,720)),
       edge('python','db',[(1330,700),(1330,500)],'SQL / тяжёлое чтение',(1345,595)),edge('async','python',[(680,810),(680,885),(1330,885),(1330,810)],'выгрузки / batch',(990,860)),
       edge('core','payment',[(490,580),(440,580),(440,990),(615,990),(615,1035)],'sync • платёжная сессия',(470,945)),edge('net','delivery',[(975,810),(975,1035)],'партнёрская передача',(990,955)),
       edge('core','delivery',[(1070,530),(1145,530),(1145,980),(1090,980),(1090,1035)],'reserveSlot • sync в C',(1148,915)),edge('bi','db',[(1700,1035),(1700,920),(1510,920),(1510,470),(1470,470)],'прямые отчётные SQL',(1535,860))]
    render('Task2/as-is','AS-IS • подтверждённые зависимости и проблемные зоны',n,e,[(40,240,1840,700,'RetailCore','#edf1f6')],['Жёлтый — существующие подсистемы. Белый — внешние участники/соседние системы. Стрелки показывают запрос или передачу данных по подписи.',
       'Скрытые риски: несколько writers статусов; Oracle как данные + логика + интеграция; ручные ветки; аналитика конкурирует с OLTP.',
       'Не схема deployment. Точные протоколы/топология и полнота интерфейсов требуют Q-08; наличие/склады известны из интервью, не полного API.'])
    n=[node('client',75,125,310,85,['Клиенты / маркетплейсы','Те же каналы и write-контракт']),node('operator',930,125,310,85,['Оператор пилота','Только чтение + legacy link']),
       node('core',85,360,360,235,['Java-ядро — сохраняется','Create / reserve / price / promo','Payment / Delivery / Status','Commands / admin в legacy','Новых бизнес-writers нет'],'#fff1cb'),
       node('db',490,370,240,150,['Oracle — сохраняется','Данные + packages','Writers: проверить Q-08'],'#fff1cb'),node('aux',85,740,645,115,['Существующие .NET / batch / Python / Admin','Staging, прямые чтения и ручные ветки пока остаются','Сначала инвентаризация; перенос по отдельным gates'],'#fff1cb'),
       node('facade',930,350,310,120,['Read facade / feature flag','Когорта → projection','Остальное / fallback → legacy'],'#ddebff'),node('capture',1490,370,320,120,['Capture (Oracle CDC)','Committed changes / W0 / W1','Только после Q-07 spike'],'#ddebff'),
       node('buffer',1490,635,320,115,['Buffer / checkpoint','Position / eventId / replay','Никаких команд партнёрам'],'#ddebff'),node('projection',1010,635,320,145,['Normalizer / read model','Provenance / coverageStart','Freshness / UNKNOWN','Источник истины — legacy'],'#ddebff'),
       node('observe',930,880,880,90,['Контроль: lag / gaps / mismatch / доступ / Oracle / checkout','Необъяснённая ошибка → rollback чтения; source data не переписываются'],'#ddebff'),
       node('partners',85,1050,645,100,['Платежи / доставка / склады / партнёры','Существующие операции сохраняются; shadow не повторяет эффекты']),node('next',1030,1050,780,100,['Следующие этапы, не scope первого cutover','Один отчёт → одна интеграция/ACL → дальнейшие seams и импортонезависимость'],'#e9ecf0')]
    e=[edge('client','core',[(230,210),(230,360)],'старый write-path',(245,310)),edge('operator','facade',[(1085,210),(1085,350)],'read-only',(1100,305)),edge('core','db',[(445,435),(490,435)],'SQL',(444,395)),
       edge('db','capture',[(730,480),(800,480),(800,540),(1430,540),(1430,440),(1490,440)],'snapshot W0 + delta • без записи обратно',(850,510)),edge('capture','buffer',[(1650,490),(1650,635)],'capture position',(1665,555)),edge('buffer','projection',[(1490,690),(1330,690)],'dedup / apply',(1335,650)),
       edge('facade','projection',[(1085,470),(1085,635)],'чтение с freshness',(1100,555)),edge('facade','core',[(930,385),(835,385),(835,300),(395,300),(395,360)],'старое чтение / fallback',(470,310)),
       edge('aux','db',[(610,740),(610,520)],'shared DB / batch',(625,600)),edge('core','partners',[(85,550),(25,550),(25,1100),(85,1100)],'сохранённые интеграции',(85,990)),
       edge('projection','observe',[(1170,780),(1170,880)],'сверка / serving watermark',(1185,822)),edge('buffer','observe',[(1650,750),(1650,880)],'lag / replay',(1665,812)),edge('projection','next',[(1330,760),(1400,760),(1400,1050)],'дальше: отдельный gate',(1415,990),True)]
    render('Task3/to-be','TO-BE первого этапа • обратимое выделение операторского чтения',n,e,[(55,245,705,735,'Legacy','#fff8e7'),(875,245,995,735,'Read-only','#eef5ff')],['Жёлтый — сохраняется; синий — добавляется для TP-01; серый — последующие этапы. Стрелки показывают запрос/данные по подписи.',
       'Capture и проекция условны: Q-03/06/07/08 и capacity/replay gates обязательны. Без доказанного захвата — legacy facade, проекция не включается.',
       'Никаких projection → Oracle writes, двойной отправки оплаты/доставки или полной замены Oracle в первом этапе.'])

if __name__ == '__main__': main()
