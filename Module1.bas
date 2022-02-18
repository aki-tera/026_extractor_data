Attribute VB_Name = "Module1"
'オブジェクト名の設定

'Option Explicit
'オプション：変数の宣言を強制するためのものらしい

'Public DosaNum As Long


Function Henshin(DosaNum As Long, DosaNumEnd As Long)
'本関数はデータシートに記入するのみ

    Attribute Henshin.VB_ProcData.VB_Invoke_Func = "m\n14"
    'カスタムショートカットキーの設定:CTRL+m

    'ループカウンタ
    Dim i As Long
    Dim j As Long

    '未使用
    'Dim kk As Long

    Dim DataHead As Long
    Dim DataEnd As Long
    Dim Datarow As Long
    Dim DataNumEnd As Long
    Dim DataNum As Long

    Dim ASNA As String
    Dim ASN3 As String
    Dim ASN4 As String
    Dim ASN5 As String
    Dim ASN6 As String

    'データ開始行
    DataHead = 72
    'DataNum = 1

    'データ選択列
    'Datarow = 5    'E列：X2だけの場合
    Datarow = 3     'C列

    '
    DosaNumEnd = 8  'X2だけの場合
    DosaNumEnd = 10

    '計算結果の入力列：
    MaRow = 8       'X2だけの場合
    MaRow = 10      'N

    '微分の結果のリミット設定：下リミット=D1、上リミット=U1
    BibunD = -5
    BibunU = 5

    'シート名称
    DosaNum = 0

    
    
    'Calrow = 7
    '先頭シートに途中経過を記入する場所
    MaClm = 68
    '現在のアクティブシート名を取得
    ASNS = ActiveSheet.Name

    i = 0
    j = 1
    'kk = 0
    '未使用

    'レーザ変位計のデータを取得していく
    '通常はC列：(1)HA-V03、X2の時はE列になるらしい    
    Do Until Cells(i + DataHead, Datarow) = ""
        '2は遅いときに変更する
        Cells(i + DataHead + 1, Datarow + MaRow + 1) = Cells(i + DataHead + 2, Datarow) - Cells(i + DataHead, Datarow)
        If Cells(i + DataHead + 1, Datarow + MaRow + 1) > BibunU Then
            Cells(i + DataHead + 1, Datarow + MaRow + 6) = "U1"
        End If
        If Cells(i + DataHead + 1, Datarow + MaRow + 1) < BibunD Then
            Cells(i + DataHead + 1, Datarow + MaRow + 2) = "D1"
        End If
        If Cells(i + DataHead + 1, Datarow + MaRow + 4) = "" Then
            If Cells(i + DataHead, Datarow + MaRow + 6) = "U1" Then
                If Cells(i + DataHead + 50, Datarow) > 5 Then
                ' 50と5の値も毎回変更する
                    If Cells(i + DataHead + 3 - 1, Datarow + MaRow + 5) = "Start" Then
                        '何もしない？
                    Else
                        Cells(i + DataHead + 3, Datarow + MaRow + 5) = "Start"
                        Cells(MaClm, 9 + j + MaRow) = j & "回目"
                        Cells(MaClm + 1, 9 + j + MaRow) = i + DataHead + 3 - 100
                        j = j + 1
                        DosaNum = j
                    End If
                End If
            End If
        End If
        i = i + 1
    Loop
    Application.ScreenUpdating = False
    '計算用シートの作成
    For k = 1 To DosaNumEnd
        Sheets.Add After:=ActiveSheet
        ActiveSheet.Name = "Data_N" & k + 2
        ASN3 = ActiveSheet.Name
        For j = 1 To DosaNum
            Worksheets(ASN3).Cells(3, 3 + j) = Worksheets(ASNS).Cells(MaClm + 1, 9 + j + MaRow)
            Worksheets(ASN3).Activate
        Next j
        '○回目、計算結果を記入していく
        j = 1
        Do Until Cells(3, 3 + j) = ""
            For i = 2 To 5001
                DaClm = Cells(3, 3 + j)
                Cells(3 + i, 3 + j) = Worksheets(ASNS).Cells(DaClm + i - 2, Datarow - 1 + k)
            Next i
            Cells(4, 3 + j) = j & "回目"
            j = j + 1
            NamaKaisuu = j
        Loop
        '計算シートのC列にインデックス追加
        For i = 2 To 5001
            Cells(3 + i, 3) = (i - 1)
        Next i
    Next k
    Application.ScreenUpdating = True
End Function


Sub Henshin_fileKurikaeshi()
    Attribute Henshin_fileKurikaeshi.VB_ProcData.VB_Invoke_Func = "m\n14"

    Dim i As Long
    Dim j As Long
    Dim kk As Long

    Dim FileHead As Long
    Dim FileEnd As Long
    Dim FileNo As Long
    Dim Datarow As Long
    Dim ASNS As String
    Dim DosaNum As Long
    Dim DosaNumEnd As Long
    Dim CheckTP(4) As Long

    '読み込むファイルの先頭から終了までの名称
    FileHead = 16
    FileEnd = 16

    '3.6sec時
    'CheckTP = 800
    'CheckTP2 = 3400

    '4.4sec時
    'CheckTP = 800
    'CheckTP2 = 3750

    'LIS4.7sec時
    'CheckTP = 4500
    'CheckTP2 = 2100

    'LIS36sec_X2時送出
    CheckTP(1) = 1100
    CheckTP(2) = 2200
    CheckTP(3) = 2940
    CheckTP(4) = 3200

    'LIS36sec_X1時送出
    CheckTP(1) = 3400
    CheckTP(2) = 1620
    CheckTP(3) = 900
    CheckTP(4) = 3200

    'LIS28sec_X1時送出
    CheckTP(1) = 2500
    CheckTP(2) = 1620
    CheckTP(3) = 850
    CheckTP(4) = 3200

    'LIS28sec_X2時送出
    CheckTP(1) = 2500
    CheckTP(2) = 1620
    CheckTP(3) = 850
    CheckTP(4) = 3200

    'LIS36sec_X2時送出
    CheckTP(1) = 3400
    CheckTP(2) = 1620
    CheckTP(3) = 900
    CheckTP(4) = 3200

    'LIS30%時送出
    CheckTP(1) = 4400
    CheckTP(2) = 2100
    CheckTP(3) = 800
    CheckTP(4) = 3200

    'LIS48sec時送出
    CheckTP(1) = 4400   'C列：X1のEND
    CheckTP(2) = 2100   'E列：X2のEND
    CheckTP(3) = 800    'D/F列：X1/X2の12mmの位置
    CheckTP(4) = 3200   'D/F列：X1/X2のHOME位置

    ThisWorkbook.Activate
    Sheets.Add After:=ActiveSheet
    ActiveSheet.Name = "位置再現性1ms"
    ASNS = ActiveSheet.Name

    j = 0

    For FileNo = FileHead To FileEnd
        FileSC = "D:Z\"
        FileHN = "auto$0$"
        FileNN = FileSC & FileHN & FileNo & ".xlsx"
        If Dir(FileNN) <> "" Then
            Workbooks.Open FileNN
        Else
            MsgBox "ファイルが存在しません。", vbExclamation
        End If
        rc = Henshin(DosaNum, DosaNumEnd)
        AName = ActiveWorkbook.Name
        For jj = 1 To 4
            For kk = 1 To DosaNumEnd
                AsName = "Data_N" & kk + 2
                Workbooks(FileHN & FileNo & ".xlsx").Activate
                ActiveWorkbook.Sheets(AsName).Select
                Cells(CheckTP(jj) + 4, 4).Select
                Range(Selection, Selection.End(xlToRight)).Select
                Selection.Copy
                ThisWorkbook.Activate
                Sheets(ASNS).Select
                ActiveSheet.Cells(3, kk + 3 + (jj - 1) * 14) = "測定位置"
                ActiveSheet.Cells(4, kk + 3 + (jj - 1) * 14) = "位置" & kk
                Cells(3, kk + 3 + (jj - 1) * 14).End(xlDown).Offset(1, 0).Select
                'ActiveSheet.Paste
                Selection.PasteSpecial Transpose:=True
                Range("A3").Select
            Next kk
        Next jj
        Workbooks(FileHN & FileNo & ".xlsx").Save
        Workbooks(FileHN & FileNo & ".xlsx").Close
        j = j + 1
    Next FileNo
End Sub










