document.write("<script type='text/javascript' src'./stub.js'></script>");
//BreadCrumb start

function InitBreadCrumb()
{
  window.stackBreadCrumb = new Array();
  var obj = new Object();
  obj.name = getCookie_faker("userId");
  obj.level = -1;
  obj.breadCrumb = "userPad";
  window.stackBreadCrumb.push(obj);
}

function SetBreadCrumb(file)
{
    InitBreadCrumb();


  if(file == null || file.hasOwnProperty('breadCrumb') && file.breadCrumb == "userPad")
  {
      return;
  }

  if(file.hasOwnProperty('breadCrumb') && file.breadCrumb == "findPad")
  {
      console.log(file);
      window.stackBreadCrumb.push(file);
       console.log(2);
      return;
  }

  var arrayTemp = new Array();
  while(file != null)
  {
      arrayTemp.push(file);
      console.log(arrayTemp);
      console.log(3);
      if(file.parentId == null || file.parentId == "")
      {
          break;
      }
      file = GetFile(file.parentId);
      //arrayTemp.push(file);
  }
  window.stackBreadCrumb = window.stackBreadCrumb.concat(arrayTemp.reverse());
  return;
}

function SetBreadCrumb1(file)
{
    //InitBreadCrumb();

  if(file == null || file.hasOwnProperty('breadCrumb') && file.breadCrumb == "userPad")
  {
      return;
  }

  if(file.hasOwnProperty('breadCrumb') && file.breadCrumb == "findPad")
  {
      console.log(file);
      window.stackBreadCrumb.push(file);
       console.log(2);
      return;
  }

  var arrayTemp = new Array();
  while(file != null)
  {
      arrayTemp.push(file);
      console.log(arrayTemp);
      console.log(3);
      if(file.parentId == null || file.parentId == "")
      {
          break;
      }
      file = GetFile(file.parentId);
      //arrayTemp.push(file);
  }
  window.stackBreadCrumb = window.stackBreadCrumb.concat(arrayTemp.reverse());
  return;
}








function ShowBreadCrumb()
{
    var html = "";
    for(var i=0;i<window.stackBreadCrumb.length;i++)
    {
      if(window.stackBreadCrumb[i].hasOwnProperty('breadCrumb') && window.stackBreadCrumb[i].breadCrumb == "userPad")
      {
        html += "<li class='userPad'><a onclick='GotoBreadCrumb("+window.stackBreadCrumb[i].id+")' style=':hover{text-decoration:underline;}'>"+window.stackBreadCrumb[i].name+"</a></li>";
        console.log(4);
        continue;
      }
      if(window.stackBreadCrumb[i].hasOwnProperty('breadCrumb') && window.stackBreadCrumb[i].breadCrumb == "findPad"){
        //console.log(window.stackBreadCrumb[i]);
        html += "<li class='findPad'><a style=':hover{text-decoration:underline;}'>"+window.stackBreadCrumb[i].name+"</a></li>";
        console.log(4);
        continue;
      }
      html += "<li class='normal'><a onclick='GotoBreadCrumb("+window.stackBreadCrumb[i].id+")' style=':hover{text-decoration:underline;}'>"+window.stackBreadCrumb[i].name+"</a></li>";
    }
    $("#breadCrumb").html(html);
}

function GotoBreadCrumb(id)
{
    GotoFile(GetFile(id));
}
//BreadCrumb end

//FindFileTable start
function getFilePath(file)
{
  var arrayTemp = new Array();
  while(file.parentId != null && file.parentId != "")
  {
    file = GetFile(file.parentId);
    if(file == null)
    {
        break;
    }
    arrayTemp.push(file);
  }
  var userPad = new Object();
	userPad.name = getCookie_faker("userId");
	userPad.id = "";
	userPad.level = -1;
	userPad.breadCrumb = "userPad";
  arrayTemp.push(userPad);
  arrayTemp.reverse();

  var path = "";
  for(var i=0;i<arrayTemp.length;i++)
  {
    path += arrayTemp[i].name;
    if(i==0)
    {
      path += ':';
      continue;
    }
    if(i==arrayTemp.length -1)
    {
      continue;
    }
    path += '/';
  }
  return path;
}

function findFile(key)
{
  var arrayFindFile = new Array();
  for(var i=0;i<window.files.length;i++)
  {
    if(isHitKey(key, window.files[i]))
    {
      var file = window.files[i];
      file.path = getFilePath(file);
      arrayFindFile.push(file);
    }
  }
  return arrayFindFile;
}

function isHitKey(key, file)
{
  if(file.name.indexOf(key) != -1)
  {
    return true;
  }
  return false;
}

function ShowFile()
{
     var table = layui.table;
    table.render({
    elem: '#table'
    ,even:true
    ,height: 'full-115'
    ,data: visiableFiles
    ,page: true //开启分页
    ,cols: [[ //表头
      {field: 'name', title: '名称', sort: true, templet: function (data) {return ShowIcon(data);}}
      ,{field: 'modifyTime', title:'修改日期', width:200, sort: true}
      ,{field: 'type', title:'类型', width:120, sort: true}
      ,{field: 'size', title:'大小', width:120, align:'right', sort: true}
      ,{field: 'right', title:'操作',width:120, align:'center', toolbar: '#bar'}
    ]]
  });
}

function ShowFindFile()
{
  var table = layui.table;
  table.render({
    elem: '#table'
    ,even:true
    ,height: 312
    ,data: window.visibleFiles
    ,page: true //开启分页
    ,cols: [[ //表头
      {field: 'name', title: '名称', width:120, sort: true, templet: function (data) {return ShowIcon(data);}}
      ,{field: 'path', title:'路径', sort: true}
      ,{field: 'modifyTime', title:'修改日期', width:200, sort: true}
      ,{field: 'type', title:'类型', width:120, sort: true}
      ,{field: 'size', title:'大小', width:120, align:'right', sort: true}
      ,{field: 'right', title:'操作',width:220, align:'center', toolbar: '#findFileBar'}
    ]]
  });
}
//FindFileTable end

//FileTable start
function InitFile()
{
	BE_InitFile_faker();
	SortFiles();
}

function SetVisiableFile(file)
{
    window.visiableFiles = new Array();

    if(file == null || file.hasOwnProperty("breadCrumb") && file.breadCrumb == "userPad")
    {
        window.visiableFiles = GetRoot();
        return;
    }

    if(file == null || file.hasOwnProperty("breadCrumb") && file.breadCrumb == "findPad")
    {
        var key = file.name.substring(1,file.name.lastIndexOf('"'));
        window.visiableFiles = findFile(key);
        return;
    }

    window.visiableFiles = GetLeafFile(file);
    return;
}

function ShowVisiableFile(file)
{
    if(file.hasOwnProperty("breadCrumb") && file.breadCrumb == "findPad")
    {
        ShowFindFile();
        return;
    }
    ShowFile();
}

function GetRoot()
{
  var arrayRoot = new Array();
  for(var i=0;i<window.files.length;i++)
  {
    if(window.files[i].parentId === "")
    {
      arrayRoot.push(window.files[i]);
    }
  }
  return arrayRoot;
}

function GetLeafFile(file)
{
  //确定是否为文件夹
  if(file.type != 'folder')
  {
    return;
  }
  var arrayLeafFile = new Array();
  for(var i=0;i<window.files.length;i++)
  {
    if(window.files[i].parentId === file.id)
    {
      arrayLeafFile.push(window.files[i]);
      //console.log(window.files[i]);
    }
  }
  return arrayLeafFile;
}

function GetFile(id)
{
    if(id == null)
    {
        var file = new Object();
        file.name = getCookie("userId");
        file.id = "";
        file.level = -1;
        file.breadCrumb = "userPad";
        return file;
    }
    for(var i=0;i<window.files.length;i++)
    {
        if(window.files[i].id === id)
        {
          return window.files[i];
        }
    }
    return;
}
//FileTable end