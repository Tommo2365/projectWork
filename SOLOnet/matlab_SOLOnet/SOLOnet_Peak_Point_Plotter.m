scatter(x,y);
grid on;
xlabel("Ambient (get) / {\it ºC}");
ylabel("SOLOnet Temperature Reading / {\it ºC}");
title('Peak Points at Stable Ambient Temperatures');
hold on

% Find linear fit coefs  
%c = polyfit(x,y,1);

% Line of best fit
%xFit = linspace(min(x), max(x));
%yFit = polyval(c , xFit);
%plt = plot(xFit, yFit, 'r-', 'LineWidth', 2);
%set(plt, 'Color', [0.929411764705882 0.694117647058824 0.125490196078431])
%hold on

% Legend
%legend('Peak Data', 'linear fit');

% y = mx+c
%annotation('textbox',...
        %[0.503571428571428 0.717289719626167 0.294642857142857 0.0628360694480757],...
        %'String',{' y = ' c(1) '*x + ' c(2)},...
        %'FitBoxToText','on',...
        %'FontWeight','bold',...
        %'FontSize',9);

hold off