% get file
matArray = csvread(uigetfile);

% Change this value to increase or decreas y-axis for response time   
yAxisAdjust = 10; % adjust integer to see more of y axis


% prompt box
prompt = {'Name of experment: Noise/Response/Ambient', 'Serial number:', 'Enter furnace set point Temperature:', 'Length of Experiment: (Time / s)'};
dlgtitle = 'Input Vaule';
bootInput = inputdlg(prompt); % input
pltName = string(bootInput{1}); % convert eleemnt 2 into string
SN = string(bootInput{2}); % serial number for save file name
tempValue = string(bootInput{3}); % convert element 2 into string (number)
lengthTime = (bootInput(4))

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  NOISE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if pltName == 'Noise' || pltName == 'n'
    pltName = 'Noise'
    % declae array
    % n = fscanf(inFile,formatSpec); % use for txt files
    yArray = matArray(:, 1);
    L = length(yArray);
    xArray = [1:1:L].';
    
    % create a time axis 
    timeSec = str2double(lengthTime)./L;
    xTime = xArray.*timeSec;
    
    % show standard deviation in command window
    stdDev = num2str(std(yArray));

    % settiing parameters for axis
    xMaxVal = max(xArray);
    %xMinVal = min(xArray);

    yMaxVal = max(yArray);
    yMinVal = min(yArray);

    yMaxPara = yMaxVal + 1;
    yMinPara = yMinVal - 1;

    % flip y-axis data upside down
    yAxis = flipud(yArray);
   
    % save file as xlsx
    A = [xTime, yAxis];

    %pltName == 'Noise'%%%%%%%%%%%%%%%%%%%%%% check this
    fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.xlsx');
    xlswrite(fileName, A);
    
    % make a plot
    nFig = figure; 
    scatter(xTime, yAxis);
    grid on;
    title([pltName,'at',tempValue,'ºC']);
    xlabel('Time / {\it s}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}');
    %legend('StdDev:', stdDev);
    xlim([0 xMaxVal + 1]);
    ylim([yMinPara yMaxPara])
    
    
    % add text to plot
    annotation(nFig,'textbox',...
        [0.850852466225819 0.197951711165462 0.0878477282003988 0.138248844263924],...
        'String',{'StdDev:', stdDev},...
        'FitBoxToText','on',...
        'FontWeight','bold',...
        'FontSize',9);

    % y - axis conditions for Noise
    ylim([yMinPara yMaxPara]); % else use these parameters
  

    % write file name a savefig
    figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.fig');
    savefig(figName)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  RESPONSE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 

elseif pltName == 'Response' || pltName == 'r'
    pltName = 'Response'
    % declae array
    %n = fscanf(inFile,formatSpec); % use for txt files
    yArray = matArray(:, 1);
    L = length(yArray);
    xArray = [1:1:L].';
    
    % create a time axis 
    timeSec = str2double(lengthTime)./L;
    xTime = xArray.*timeSec;
    
    % Find 90% of most common value
    mode = mode(yArray);
    percentile = mode*0.9;
    
    % show standard deviation in command window
    stdDev = std(yArray);
    
    % settiing parameters for axis
    xMaxVal = max(xArray);
    xMinVal = min(xArray);

    yMaxVal = max(yArray);
    yMinVal = min(yArray);

    yMaxPara = yMaxVal + 1;
    yMinPara = yMinVal - 1;

    yMedVal = median(yArray) - yAxisAdjust; % adjust integer to see more of y axis

    % save file as xlsx

    % flip y-axis data upside down
    yAxis = flipud(yArray);

    A = [xTime, yAxis];

    %pltName == 'Response'
    fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.xlsx');
    xlswrite(fileName, A);
   
    % full plot to check next plot is zoomed in at sutibale location (y - axis)
    rFig1 = subplot(1,2,1);
    scatter(xTime, yAxis);
    grid on;
    title([pltName,' at ',tempValue,'ºC']);
    xlabel('Time / {\it s}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}');
    %%legend('StdDev:', num2str(stdDev));
    %xlim([0 120]);
    
    
    % make a plot
    rFig2 = subplot(1,2,2);
    scatter(xTime, yAxis);
    grid on;
    title([pltName,' at ',tempValue,'ºC']);
    xlabel('Time / {\it s}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}');
    %xlim([0 120]);
    ylim([550 yMaxPara]);  % use median to find approriate axis
    
    % write file name a savefig
    figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.fig');
    savefig(figName)
    
    %saveas(fig1,figName,'.jpg' ,jpg)
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  AMBIENT  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

elseif pltName == 'Ambient' || pltName == 'a'
    prompt = {'Enter furnace temperature(Cyclops):', 'Number of steps:', 'Serial number: ', 'Length of Experiment: (Time / mins)'};
    pltName = 'Ambient'
    
    %dlgtitle = 'Input Vaule';
    input = inputdlg(prompt);      % input
    tempValue = str2num(input{1}); % convert element 'N' into number
    stepCount = str2num(input{2});
    SN = input{3};                 % for use in save file name
    time = str2num(input{3});      

    % declare array (:, axis number)
    xAxis = matArray(:, 1);
    yAxis = matArray(:, 2);

    % set up condtions
    xSum = sum(xAxis);
    eSum = sum(yAxis);

    % create a time axis 
    mins2secs = 60
    timeSec = L./str2double(lengthTime);
    xTime = xArray.*timeSec.*mins2secs;
    
    % swap columns if conditions are met
    if (xSum > eSum)
        yAxis = matArray(:, 1);
        xAxis = matArray(:, 2);
    end

    % subtract furnTemp from yAxis 
    if yAxis == matArray(:, 1);
        Error = yAxis - tempValue;
    elseif xAxis == matArray(:, 1);
        Error = yAxis - tempValue;
    end

    % flip columns upsided down (data input is formated upside down prior)
    x = flipud(xAxis);
    yn = flipud(yAxis);
    y = flipud(Error);

    % Find the maximum drift
    driftError = max(y)-min(y)
    driftError2 = num2str(driftError);

    % combine matrix axis
    A = [x,yn,y]; 
    
    % write file names and save data as xlsx
    if stepCount >= 2
        Filename = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_STEP_', SN, '.xlsx' );
        xlswrite(Filename, A);
    elseif stepCount < 2
        Filename = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_', SN, '.xlsx' );
        xlswrite(Filename, A);
    end

    % write file names and save plt as .fig
    if stepCount >= 2
        figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_STEP_', SN, '.fig');
    elseif stepCount < 2
        figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_', SN, '.fig');
    end

    L = length(A);
    %sixty = [60::L].';
    time = [1/60:1/60:L/60].';
    
    % plot data
    aFig1 = subplot(2,1,1);
    scatter(x, y);
    grid on;
    hold on
    e1 = plot([5 50], [3 -7], 'LineWidth',2);
    e1.Color = 'r';
    hold on
    e2 = plot([5 50], [-3 7], 'LineWidth',2);
    e2.Color = 'r';
    legend1 = legend('Drift','Spec','Spec');
    set(legend1,'Position',[0.85362164058084 0.505700114698771 0.127009644960667 0.119638822955956]);
    title('Ambient Response');
    xlabel('Ambient (get) / {\it ºC}');
    ylabel('Error / {\it ºC}' );
    
   
    % sub plot vs time
    aFig2 = subplot(2,1,2);
    yyaxis left
    scatter(time, yn);
    grid on;
    xlabel('Time / {\it mins}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}' );
    hold on;
    yyaxis right
    plot(time, x);
    ylabel('Ambient (get) / {\it ºC}');
    
 % add text to plot
    %annotation(aFig1,'textbox',...
        %[0.850852466225819 0.197951711165462 0.0878477282003988 0.138248844263924],...
        %'String',{'Number of steps:',(input{2}), '', 'Max Drift Error / {\it ºC}:',driftError2},...
        %'FitBoxToText','on',...
        %'FontWeight','bold',...
        %'FontSize',9);
    

    savefig(figName);
    
    %figPGN = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_', SN, '.pgn');
    
    %save(fileName)

end
